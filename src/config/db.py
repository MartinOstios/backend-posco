from sqlmodel import Session, create_engine, select, SQLModel

from src.crud import employee as employee_crud
from src.crud import enterprise as enterprise_crud
from src.crud import role as role_crud
from src.crud import supplier as supplier_crud
from src.crud import category as category_crud
from src.crud import product as product_crud
from src.config.settings import settings

# Importar todos los modelos
from src.models import *

engine = create_engine(settings.MYSQL_URI)

def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)
    
    # Crear empresa inicial si no existe
    enterprise = session.exec(
        select(Enterprise).where(Enterprise.NIT == settings.FIRST_ENTERPRISE_NIT)
    ).first()
    if not enterprise:
        enterprise_in = EnterpriseCreate(
            name=settings.FIRST_ENTERPRISE_NAME,
            NIT=settings.FIRST_ENTERPRISE_NIT,
            email=settings.FIRST_ENTERPRISE_EMAIL,
            phone_number=settings.FIRST_ENTERPRISE_PHONE,
            currency="COP"
        )
        enterprise = enterprise_crud.create(session=session, obj_in=enterprise_in)

    # Crear rol admin si no existe
    admin_role = session.exec(select(Role).where(Role.name == "ADMIN")).first()
    if not admin_role:
        admin_role = role_crud.create(
            session=session,
            obj_in=RoleCreate(
                name="ADMIN",
                description="Administrador del sistema"
            )
        )

    # Crear empleado inicial si no existe
    employee = session.exec(
        select(Employee).where(Employee.email == settings.FIRST_SUPERUSER)
    ).first()
    if not employee:
        employee_in = EmployeeCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            name="Admin",
            lastname="System",
            code="ADMIN001",
            telephone="0000000000",
            enterprise_id=enterprise.id,
            role_id=admin_role.id
        )
        employee = employee_crud.create(session=session, obj_in=employee_in)

    # Crear proveedor por defecto si no existe
    supplier = session.exec(
        select(Supplier).where(
            Supplier.NIT == "987654321-0",
            Supplier.enterprise_id == enterprise.id
        )
    ).first()
    if not supplier:
        supplier_in = SupplierCreate(
            name="Distribuidora Nacional",
            email="contacto@distribuidora.com",
            NIT="987654321-0",
            phone_number="3001234567",
            enterprise_id=enterprise.id
        )
        supplier = supplier_crud.create(session=session, obj_in=supplier_in)

    # Crear categorías por defecto si no existen
    categories_data = [
        ("Bebidas", "Refrescos, jugos y bebidas"),
        ("Snacks", "Papas fritas, galletas y botanas"),
        ("Lácteos", "Leche, quesos y yogurt")
    ]

    categories = []
    for name, description in categories_data:
        category = session.exec(
            select(Category).where(
                Category.name == name,
                Category.enterprise_id == enterprise.id
            )
        ).first()
        if not category:
            category_in = CategoryCreate(
                name=name,
                description=description,
                enterprise_id=enterprise.id
            )
            category = category_crud.create(session=session, obj_in=category_in)
        categories.append(category)

    # Crear productos por defecto si no existen
    products_data = [
        # Bebidas
        {
            "name": "Coca Cola 500ml",
            "description": "Refresco carbonatado",
            "bar_code": "7501234567890",
            "supplier_price": 2000,
            "public_price": 2500,
            "stock": 100,
            "minimal_safe_stock": 20,
            "category_index": 0,
            "status": 'active',
            "thumbnail": "coca_cola.jpg",
            "discount": 0
        },
        {
            "name": "Pepsi 500ml",
            "description": "Refresco carbonatado",
            "bar_code": "7501234567891",
            "supplier_price": 1900,
            "public_price": 2400,
            "stock": 80,
            "minimal_safe_stock": 15,
            "category_index": 0,
            "status": 'active',
            "thumbnail": "pepsi.jpg",
            "discount": 0
        },
        {
            "name": "Jugo de Naranja 1L",
            "description": "Jugo natural",
            "bar_code": "7501234567892",
            "supplier_price": 3500,
            "public_price": 4000,
            "stock": 50,
            "minimal_safe_stock": 10,
            "category_index": 0,
            "status": 'active',
            "thumbnail": "jugo_naranja.jpg",
            "discount": 0
        },
        # Snacks
        {
            "name": "Doritos 45g",
            "description": "Tortillas de maíz",
            "bar_code": "7501234567893",
            "supplier_price": 1500,
            "public_price": 1800,
            "stock": 150,
            "minimal_safe_stock": 30,
            "category_index": 1,
            "status": 'active',
            "thumbnail": "doritos.jpg",
            "discount": 0
        },
        {
            "name": "Cheetos 45g",
            "description": "Snack de maíz",
            "bar_code": "7501234567894",
            "supplier_price": 1400,
            "public_price": 1700,
            "stock": 120,
            "minimal_safe_stock": 25,
            "category_index": 1,
            "status": 'active',
            "thumbnail": "cheetos.jpg",
            "discount": 0
        },
        {
            "name": "Galletas Oreo",
            "description": "Galletas de chocolate",
            "bar_code": "7501234567895",
            "supplier_price": 1700,
            "public_price": 2000,
            "stock": 200,
            "minimal_safe_stock": 40,
            "category_index": 1,
            "status": 'active',
            "thumbnail": "oreo.jpg",
            "discount": 0
        },
        # Lácteos
        {
            "name": "Leche Entera 1L",
            "description": "Leche de vaca",
            "bar_code": "7501234567896",
            "supplier_price": 3000,
            "public_price": 3500,
            "stock": 80,
            "minimal_safe_stock": 20,
            "category_index": 2,
            "status": 'active',
            "thumbnail": "leche.jpg",
            "discount": 0
        },
        {
            "name": "Yogurt Natural 1L",
            "description": "Yogurt sin azúcar",
            "bar_code": "7501234567897",
            "supplier_price": 4000,
            "public_price": 4500,
            "stock": 40,
            "minimal_safe_stock": 10,
            "category_index": 2,
            "status": 'active',
            "thumbnail": "yogurt.jpg",
            "discount": 0
        },
        {
            "name": "Queso Mozzarella 500g",
            "description": "Queso fresco",
            "bar_code": "7501234567898",
            "supplier_price": 10000,
            "public_price": 12000,
            "stock": 30,
            "minimal_safe_stock": 8,
            "category_index": 2,
            "status": 'active',
            "thumbnail": "queso.jpg",
            "discount": 0
        },
        {
            "name": "Mantequilla 250g",
            "description": "Mantequilla sin sal",
            "bar_code": "7501234567899",
            "supplier_price": 5000,
            "public_price": 5500,
            "stock": 45,
            "minimal_safe_stock": 12,
            "category_index": 2,
            "status": 'active',
            "thumbnail": "mantequilla.jpg",
            "discount": 0
        }
    ]

    for product_data in products_data:
        product = session.exec(
            select(Product).where(
                Product.bar_code == product_data["bar_code"],
                Product.enterprise_id == enterprise.id
            )
        ).first()
        if not product:
            product_in = ProductCreate(
                name=product_data["name"],
                description=product_data["description"],
                bar_code=product_data["bar_code"],
                supplier_price=product_data["supplier_price"],
                public_price=product_data["public_price"],
                stock=product_data["stock"],
                minimal_safe_stock=product_data["minimal_safe_stock"],
                enterprise_id=enterprise.id,
                category_id=categories[product_data["category_index"]].id,
                supplier_id=supplier.id,
                status=product_data["status"],
                thumbnail=product_data["thumbnail"],
                discount=product_data["discount"]
            )
            product_crud.create(session=session, obj_in=product_in)
