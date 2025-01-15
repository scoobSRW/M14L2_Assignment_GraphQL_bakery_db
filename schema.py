import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Product as ProductModel, db
from sqlalchemy.orm import Session

class Product(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel

class Query(graphene.ObjectType):
    products = graphene.List(Product)

    def resolve_products(self, info):
        return db.session.execute(db.select(ProductModel)).scalars().all()

class AddProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        quantity = graphene.Int(required=True)
        category = graphene.String(required=True)
        baker = graphene.String(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, name, price, quantity, category, baker):
        with Session(db.engine) as session:
            with session.begin():
                product = ProductModel(name=name, price=price, quantity=quantity, category=category, baker=baker)
                session.add(product)
            session.refresh(product)
            return AddProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        quantity = graphene.Int(required=True)
        category = graphene.String(required=True)
        baker = graphene.String(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, id, name=None, price=None, quantity=None, category=None, baker=None):
        with Session(db.engine) as session:
            with session.begin():
                product = session.execute(db.select(ProductModel).where(ProductModel.id == id)).scalars().first()
                if not product:
                    return None
                if name:
                    product.name = name
                if price:
                    product.price = price
                if quantity:
                    product.quantity = quantity
                if category:
                    product.category = category
                if baker:
                    product.baker = baker
            session.refresh(product)
            return UpdateProduct(product=product)

class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, id):
        with Session(db.engine) as session:
            with session.begin():
                product = session.execute(db.select(ProductModel).where(ProductModel.id == id)).scalars().first()
                if not product:
                    return None
                session.delete(product)
            return DeleteProduct(product=None)  # Indicate deletion success.

class Mutation(graphene.ObjectType):
    create_product = AddProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)