from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class Device(db.Model):
    __tablename__ = 'device'
    device_id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    device_name = db.Column(db.String(255), nullable=False)
    external_bucket_id = db.Column(db.String(255))
    latitude = db.Column(db.Numeric(10, 6))
    longitude = db.Column(db.Numeric(10, 6))

class Setting(db.Model):
    __tablename__ = 'setting'
    setting_id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    device_id = db.Column(db.String(36), db.ForeignKey('device.device_id'), unique=True, nullable=False)
    ip = db.Column(db.String(45), nullable=False)  # Change 'Ip' to 'ip'
    port = db.Column(db.Integer, nullable=False)
    slave_id = db.Column(db.Integer)



class Tag(db.Model):
    __tablename__ = 'tag'
    tag_id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    device_id = db.Column(db.String(36), db.ForeignKey('device.device_id'), nullable=False)
    tag_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    register = db.Column(db.Integer, nullable=False)


class DescriptionDevice(db.Model):
    __tablename__ = 'description_device'  # Убедитесь, что имя таблицы совпадает с именем в вашей базе данных
    description_id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    device_id = db.Column(db.String(36), db.ForeignKey('device.device_id'), nullable=False)
    description_name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
