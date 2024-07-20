from app import db, app
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, UTC


class TbDevices(db.Model):
    __tablename__ = 'tb_devices'
    id_device: Mapped[str] = mapped_column(db.String(30), primary_key=True)
    temp_limit_upper: Mapped[int] = mapped_column(db.Float, nullable=False)
    temp_limit_lower: Mapped[int] = mapped_column(db.Float, nullable=False)
    temp_limit_setting: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_limit_upper: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_limit_lower: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_limit_setting: Mapped[int] = mapped_column(db.Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.TIMESTAMP (timezone=True), default=lambda : datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.TIMESTAMP (timezone=True),
        default=lambda : datetime.now(UTC),
        onupdate=lambda : datetime.now(UTC),
    )


class TbRegisters(db.Model):
    __tablename__ = 'tb_registers'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_device: Mapped[str] = mapped_column(db.String(30), nullable=False)
    temp_value: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_value: Mapped[int] = mapped_column(db.Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.TIMESTAMP (timezone=True), default=lambda : datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.TIMESTAMP (timezone=True),
        default=lambda : datetime.now(UTC),
        onupdate=lambda : datetime.now(UTC),
    )


class TbHistory(db.Model):
    __tablename__ = 'tb_history'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    id_device: Mapped[str] = mapped_column(db.String(30), nullable=False)
    action: Mapped[str] = mapped_column(db.String(10), nullable=False)
    temp_limit_upper: Mapped[int] = mapped_column(db.Float, nullable=False)
    temp_limit_lower: Mapped[int] = mapped_column(db.Float, nullable=False)
    temp_limit_setting: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_limit_upper: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_limit_lower: Mapped[int] = mapped_column(db.Float, nullable=False)
    humi_limit_setting: Mapped[int] = mapped_column(db.Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.TIMESTAMP (timezone=True), default=lambda : datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.TIMESTAMP (timezone=True),
        default=lambda : datetime.now(UTC),
        onupdate=lambda : datetime.now(UTC),
    )

def create_database():
    try:
        with app.app_context():
            db.create_all()
    except:
        pass