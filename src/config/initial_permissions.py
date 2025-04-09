from sqlmodel import Session, select
from src.models import Role, Permission, PermissionHasRole

def create_initial_permissions(session: Session) -> None:
    # Crear permisos básicos
    permissions = [
        Permission(name="GESTIONAR_EMPLEADOS", description="Gestionar empleados del sistema"),
        Permission(name="GESTIONAR_INVENTARIO", description="Gestionar inventario"),
        Permission(name="GESTIONAR_VENTAS", description="Gestionar ventas"),
        Permission(name="VER_REPORTES", description="Ver reportes financieros"),
        Permission(name="GESTIONAR_PROVEEDORES", description="Gestionar proveedores del sistema"),
    ]

    # Verificar si ya existen los permisos
    existing_permissions = session.query(Permission).all()
    existing_permission_names = [p.name for p in existing_permissions]

    # Filtrar solo los permisos que no existen
    permissions = [
        p for p in permissions 
        if p.name not in existing_permission_names
    ]

    if not permissions:
        return
    
    for permission in permissions:
        session.add(permission)
    
    session.commit()

def create_initial_roles(session: Session) -> None:
    # Verificar si los roles ya existen
    existing_roles = session.query(Role).all()
    existing_role_names = [r.name for r in existing_roles]

    # Eliminar el rol USER si existe
    user_role = session.exec(select(Role).where(Role.name == "USER")).first()
    if user_role:
        session.delete(user_role)
        session.commit()

    # Crear o actualizar rol ADMIN
    admin_role = session.exec(select(Role).where(Role.name == "ADMIN")).first()
    if not admin_role:
        admin_role = Role(name="ADMIN", description="Administrador del sistema")
        session.add(admin_role)
        session.commit()

    # Asignar todos los permisos al rol admin
    permissions = session.query(Permission).all()
    existing_admin_permissions = session.query(PermissionHasRole).filter(
        PermissionHasRole.role_id == admin_role.id
    ).all()
    existing_admin_permission_ids = [p.permission_id for p in existing_admin_permissions]

    for permission in permissions:
        if permission.id not in existing_admin_permission_ids:
            permission_role = PermissionHasRole(
                permission_id=permission.id,
                role_id=admin_role.id
            )
            session.add(permission_role)
    session.commit()

    # Crear o actualizar rol EMPLEADO
    employee_role = session.exec(select(Role).where(Role.name == "EMPLEADO")).first()
    if not employee_role:
        employee_role = Role(name="EMPLEADO", description="Empleado del sistema")
        session.add(employee_role)
        session.commit()

    # Asignar permisos al rol EMPLEADO
    employee_permissions = ["GESTIONAR_INVENTARIO", "VER_REPORTES"]
    permissions = session.query(Permission).filter(Permission.name.in_(employee_permissions)).all()
    
    # Limpiar permisos existentes
    session.query(PermissionHasRole).filter(PermissionHasRole.role_id == employee_role.id).delete()
    
    for permission in permissions:
        permission_role = PermissionHasRole(
            permission_id=permission.id,
            role_id=employee_role.id
        )
        session.add(permission_role)
    session.commit()

    # Crear o actualizar rol VENDEDOR
    seller_role = session.exec(select(Role).where(Role.name == "VENDEDOR")).first()
    if not seller_role:
        seller_role = Role(name="VENDEDOR", description="Vendedor del sistema")
        session.add(seller_role)
        session.commit()

    # Asignar permisos al rol VENDEDOR
    seller_permissions = ["GESTIONAR_VENTAS"]
    permissions = session.query(Permission).filter(Permission.name.in_(seller_permissions)).all()
    
    # Limpiar permisos existentes
    session.query(PermissionHasRole).filter(PermissionHasRole.role_id == seller_role.id).delete()
    
    for permission in permissions:
        permission_role = PermissionHasRole(
            permission_id=permission.id,
            role_id=seller_role.id
        )
        session.add(permission_role)
    session.commit()