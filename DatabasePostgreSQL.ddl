CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE Device (
    Device_Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Device_name VARCHAR(255) NOT NULL,
    External_bucket_Id = db.Column(db.String(255), nullable=True)
    Latitude DECIMAL(10,6),
    Longitude DECIMAL(10,6)
);

CREATE TABLE Setting (
    Setting_Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Device_id UUID UNIQUE REFERENCES Device(Device_Id) ON DELETE CASCADE,
    Ip VARCHAR(45) NOT NULL,
    Port INTEGER NOT NULL,
    Slave_id INTEGER
);

CREATE TABLE Tag (
    Tag_Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Device_Id UUID REFERENCES Device(Device_Id) ON DELETE CASCADE,
    Tag_name VARCHAR(255) NOT NULL,
    Description TEXT,
    Register INT NOT NULL
);

CREATE TABLE Description_Device (
    Description_Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Device_Id UUID REFERENCES Device(Device_Id) ON DELETE CASCADE,
    Description_Name VARCHAR(255) not NULL,
    Content TEXT
);
