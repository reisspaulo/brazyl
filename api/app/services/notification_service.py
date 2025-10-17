"""
Service de Notificações - Lógica de negócio para notificações via WhatsApp.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from app.integrations import get_supabase, SupabaseClientError
from app.integrations.transparencia_api import AvisaAPI
from app.schemas.notification import NotificationCreate, NotificationStatus
from app.utils.logger import setup_logger
from app.utils.formatters import format_datetime_br, format_currency, truncate_text

logger = setup_logger(__name__)


class NotificationServiceError(Exception):
    """Exceção para erros do serviço de notificações."""
    pass


class NotificationService:
    """Service para operações com notificações."""
    
    def __init__(self):
        """Inicializa o service."""
        self.supabase = get_supabase()
        self.avisa = AvisaAPI()
    
    async def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> dict:
        """
        Cria uma nova notificação.
        
        Args:
            notification_data: Dados da notificação
        
        Returns:
            Notificação criada
        
        Raises:
            NotificationServiceError: Se houver erro
        """
        try:
            logger.info(f"Criando notificação para usuário: {notification_data.user_id}")
            
            # Verificar se usuário existe
            user = await self.supabase.client.table("users")\
                .select("id, whatsapp_number")\
                .eq("id", str(notification_data.user_id))\
                .maybe_single()\
                .execute()
            
            if not user.data:
                raise NotificationServiceError("Usuário não encontrado")
            
            # Preparar dados
            db_data = {
                "user_id": str(notification_data.user_id),
                "politician_id": str(notification_data.politician_id) if notification_data.politician_id else None,
                "event_id": str(notification_data.event_id) if notification_data.event_id else None,
                "title": notification_data.title,
                "message": notification_data.message,
                "scheduled_for": notification_data.scheduled_for.isoformat() if notification_data.scheduled_for else None,
                "metadata": notification_data.metadata or {}
            }
            
            # Criar notificação
            notification = await self.supabase.create_notification(db_data)
            
            # Se não tem agendamento, enviar imediatamente
            if not notification_data.scheduled_for:
                await self.send_notification(notification["id"])
            
            logger.info(f"Notificação criada: {notification['id']}")
            return notification
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao criar notificação: {str(e)}")
            raise NotificationServiceError(f"Erro ao criar notificação: {str(e)}")
    
    async def send_notification(self, notification_id: UUID) -> bool:
        """
        Envia uma notificação via WhatsApp.
        
        Args:
            notification_id: ID da notificação
        
        Returns:
            True se enviada com sucesso
        
        Raises:
            NotificationServiceError: Se houver erro
        """
        try:
            logger.info(f"Enviando notificação: {notification_id}")
            
            # Buscar notificação com dados do usuário
            notification = await self.supabase.client.table("notifications")\
                .select("*, users(whatsapp_number)")\
                .eq("id", str(notification_id))\
                .single()\
                .execute()
            
            if not notification.data:
                raise NotificationServiceError("Notificação não encontrada")
            
            notif_data = notification.data
            whatsapp = notif_data.get("users", {}).get("whatsapp_number")
            
            if not whatsapp:
                raise NotificationServiceError("WhatsApp do usuário não encontrado")
            
            # Formatar mensagem
            formatted_message = self._format_message(
                notif_data.get("title"),
                notif_data.get("message")
            )
            
            # Atualizar status para SENT
            await self.supabase.update_notification_status(
                str(notification_id),
                NotificationStatus.SENT.value,
                sent_at=datetime.utcnow().isoformat()
            )
            
            # Enviar via Avisa API
            try:
                response = await self.avisa.send_message(
                    phone=whatsapp,
                    message=formatted_message
                )
                
                # Atualizar status para DELIVERED
                await self.supabase.update_notification_status(
                    str(notification_id),
                    NotificationStatus.DELIVERED.value,
                    delivered_at=datetime.utcnow().isoformat()
                )
                
                logger.info(f"Notificação enviada com sucesso: {notification_id}")
                return True
            
            except Exception as e:
                # Atualizar status para FAILED
                await self.supabase.update_notification_status(
                    str(notification_id),
                    NotificationStatus.FAILED.value,
                    error_message=str(e)
                )
                
                logger.error(f"Erro ao enviar notificação via WhatsApp: {str(e)}")
                raise NotificationServiceError(f"Erro ao enviar via WhatsApp: {str(e)}")
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao processar notificação: {str(e)}")
            raise NotificationServiceError(f"Erro ao processar notificação: {str(e)}")
    
    async def get_user_notifications(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[dict], int]:
        """
        Lista notificações de um usuário.
        
        Args:
            user_id: ID do usuário
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Tupla (lista de notificações, total)
        """
        try:
            logger.info(f"Listando notificações do usuário: {user_id}")
            
            response = await self.supabase.client.table("notifications")\
                .select("*, politicians(parliamentary_name)", count="exact")\
                .eq("user_id", str(user_id))\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            total = response.count or 0
            notifications = response.data or []
            
            # Adicionar nome do político
            for notif in notifications:
                if notif.get("politicians"):
                    notif["politician_name"] = notif["politicians"].get("parliamentary_name")
            
            return notifications, total
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao listar notificações: {str(e)}")
            raise NotificationServiceError(f"Erro ao listar notificações: {str(e)}")
    
    async def get_notification_stats(self, user_id: UUID) -> dict:
        """
        Obtém estatísticas de notificações de um usuário.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Estatísticas de notificações
        """
        try:
            logger.info(f"Obtendo estatísticas de notificações: {user_id}")
            
            # Buscar todas as notificações
            response = await self.supabase.client.table("notifications")\
                .select("status, created_at")\
                .eq("user_id", str(user_id))\
                .execute()
            
            notifications = response.data or []
            
            # Calcular estatísticas
            stats = {
                "total": len(notifications),
                "pending": 0,
                "sent": 0,
                "delivered": 0,
                "failed": 0,
                "last_notification_at": None
            }
            
            for notif in notifications:
                status = notif.get("status", "").upper()
                
                if status == NotificationStatus.PENDING.value:
                    stats["pending"] += 1
                elif status == NotificationStatus.SENT.value:
                    stats["sent"] += 1
                elif status == NotificationStatus.DELIVERED.value:
                    stats["delivered"] += 1
                elif status == NotificationStatus.FAILED.value:
                    stats["failed"] += 1
            
            # Última notificação
            if notifications:
                stats["last_notification_at"] = notifications[0].get("created_at")
            
            return stats
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise NotificationServiceError(f"Erro ao obter estatísticas: {str(e)}")
    
    async def process_pending_notifications(self) -> int:
        """
        Processa notificações pendentes agendadas.
        Deve ser chamado por um cron job.
        
        Returns:
            Número de notificações processadas
        """
        try:
            logger.info("Processando notificações pendentes...")
            
            # Buscar notificações pendentes que já passaram do horário
            now = datetime.utcnow().isoformat()
            
            response = await self.supabase.client.table("notifications")\
                .select("id")\
                .eq("status", NotificationStatus.PENDING.value)\
                .lte("scheduled_for", now)\
                .limit(100)\
                .execute()
            
            notifications = response.data or []
            processed = 0
            
            for notif in notifications:
                try:
                    await self.send_notification(notif["id"])
                    processed += 1
                except Exception as e:
                    logger.error(f"Erro ao processar notificação {notif['id']}: {str(e)}")
            
            logger.info(f"Processadas {processed} notificações")
            return processed
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao processar notificações pendentes: {str(e)}")
            return 0
    
    def _format_message(self, title: str, message: str) -> str:
        """
        Formata mensagem para WhatsApp.
        
        Args:
            title: Título da notificação
            message: Mensagem
        
        Returns:
            Mensagem formatada
        """
        formatted = f"*🇧🇷 Brazyl - Acompanhe Políticos*\n\n"
        formatted += f"*{title}*\n\n"
        formatted += f"{message}\n\n"
        formatted += f"_Enviado em {format_datetime_br(datetime.now())}_"
        
        return formatted

