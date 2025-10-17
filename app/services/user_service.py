"""
Service de Usuários - Lógica de negócio relacionada a usuários.
"""

from typing import Optional
from uuid import UUID

from app.integrations import get_supabase, SupabaseClientError
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PlanType
from app.utils.logger import setup_logger
from app.utils.validators import validate_whatsapp_number, validate_cpf
from app.utils.formatters import format_whatsapp_number

logger = setup_logger(__name__)


class UserServiceError(Exception):
    """Exceção para erros do serviço de usuários."""
    pass


class UserService:
    """Service para operações com usuários."""
    
    def __init__(self):
        """Inicializa o service."""
        self.supabase = get_supabase()
    
    async def create_user(self, user_data: UserCreate) -> dict:
        """
        Cria um novo usuário.
        
        Args:
            user_data: Dados do usuário a criar
        
        Returns:
            Usuário criado
        
        Raises:
            UserServiceError: Se houver erro na criação
        """
        try:
            # Formatar WhatsApp
            formatted_whatsapp = format_whatsapp_number(user_data.whatsapp_number)
            
            # Validar WhatsApp
            if not validate_whatsapp_number(formatted_whatsapp):
                raise UserServiceError("Número de WhatsApp inválido")
            
            # Validar CPF se fornecido
            if user_data.cpf and not validate_cpf(user_data.cpf):
                raise UserServiceError("CPF inválido")
            
            # Verificar se usuário já existe
            existing_user = await self.supabase.get_user_by_whatsapp(formatted_whatsapp)
            if existing_user:
                raise UserServiceError("Usuário já cadastrado com este WhatsApp")
            
            # Buscar plano padrão (FREE)
            plan_query = await self.supabase.client.table("plans")\
                .select("id")\
                .eq("type", user_data.plan_type.value)\
                .single()\
                .execute()
            
            if not plan_query.data:
                raise UserServiceError("Plano não encontrado")
            
            plan_id = plan_query.data["id"]
            
            # Preparar dados
            db_data = {
                "whatsapp_number": formatted_whatsapp,
                "name": user_data.name,
                "email": user_data.email,
                "cpf": user_data.cpf,
                "plan_id": plan_id,
                "preferences": user_data.preferences.model_dump() if user_data.preferences else {}
            }
            
            # Criar usuário
            logger.info(f"Criando usuário: {user_data.name}")
            user = await self.supabase.create_user(db_data)
            
            logger.info(f"Usuário criado com sucesso: {user['id']}")
            return user
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            raise UserServiceError(f"Erro ao criar usuário: {str(e)}")
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[dict]:
        """
        Obtém usuário por ID.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dados do usuário ou None
        """
        try:
            logger.info(f"Buscando usuário: {user_id}")
            
            response = await self.supabase.client.table("users")\
                .select("*, plans(*)")\
                .eq("id", str(user_id))\
                .maybe_single()\
                .execute()
            
            return response.data
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao buscar usuário: {str(e)}")
            return None
    
    async def get_user_by_whatsapp(self, whatsapp: str) -> Optional[dict]:
        """
        Obtém usuário por WhatsApp.
        
        Args:
            whatsapp: Número de WhatsApp
        
        Returns:
            Dados do usuário ou None
        """
        try:
            formatted_whatsapp = format_whatsapp_number(whatsapp)
            return await self.supabase.get_user_by_whatsapp(formatted_whatsapp)
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao buscar usuário por WhatsApp: {str(e)}")
            return None
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> dict:
        """
        Atualiza dados do usuário.
        
        Args:
            user_id: ID do usuário
            user_data: Dados a atualizar
        
        Returns:
            Usuário atualizado
        
        Raises:
            UserServiceError: Se houver erro na atualização
        """
        try:
            # Validar CPF se fornecido
            if user_data.cpf and not validate_cpf(user_data.cpf):
                raise UserServiceError("CPF inválido")
            
            # Preparar dados (apenas campos fornecidos)
            db_data = {}
            
            if user_data.name is not None:
                db_data["name"] = user_data.name
            if user_data.email is not None:
                db_data["email"] = user_data.email
            if user_data.cpf is not None:
                db_data["cpf"] = user_data.cpf
            if user_data.preferences is not None:
                db_data["preferences"] = user_data.preferences.model_dump()
            if user_data.is_active is not None:
                db_data["is_active"] = user_data.is_active
            
            if not db_data:
                raise UserServiceError("Nenhum dado para atualizar")
            
            logger.info(f"Atualizando usuário: {user_id}")
            user = await self.supabase.update_user(str(user_id), db_data)
            
            logger.info(f"Usuário atualizado com sucesso: {user_id}")
            return user
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            raise UserServiceError(f"Erro ao atualizar usuário: {str(e)}")
    
    async def check_user_limits(self, user_id: UUID) -> dict:
        """
        Verifica limites do usuário baseado no plano.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Dicionário com informações de limites
        """
        try:
            # Buscar usuário com plano
            user = await self.get_user_by_id(user_id)
            
            if not user:
                raise UserServiceError("Usuário não encontrado")
            
            plan = user.get("plans", {})
            max_politicians = plan.get("max_politicians", 0)
            
            # Contar políticos seguidos
            follows, total = await self.supabase.get_user_follows(str(user_id), limit=1)
            
            remaining = max_politicians - total
            
            logger.info(f"Limites do usuário {user_id}: {total}/{max_politicians} políticos")
            
            return {
                "max_politicians": max_politicians,
                "current_following": total,
                "remaining": max(0, remaining),
                "can_follow_more": remaining > 0,
                "plan_type": plan.get("type"),
                "plan_name": plan.get("name")
            }
        
        except SupabaseClientError as e:
            logger.error(f"Erro ao verificar limites: {str(e)}")
            raise UserServiceError(f"Erro ao verificar limites: {str(e)}")
    
    async def can_follow_politician(self, user_id: UUID) -> bool:
        """
        Verifica se usuário pode seguir mais políticos.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            True se pode seguir, False caso contrário
        """
        try:
            limits = await self.check_user_limits(user_id)
            return limits["can_follow_more"]
        
        except UserServiceError:
            return False

