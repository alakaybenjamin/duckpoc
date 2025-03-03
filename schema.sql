-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR(256),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Studies table
CREATE TABLE clinical_study (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    phase VARCHAR(50),
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    relevance_score FLOAT DEFAULT 1.0,
    indication_category VARCHAR(100),
    procedure_category VARCHAR(100),
    severity VARCHAR(50),
    risk_level VARCHAR(50),
    duration INTEGER
);

-- Indications table
CREATE TABLE indication (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    category VARCHAR(100),
    severity VARCHAR(50),
    relevance_score FLOAT DEFAULT 1.0
);

-- Procedures table
CREATE TABLE procedure (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    category VARCHAR(100),
    risk_level VARCHAR(50),
    duration INTEGER,
    relevance_score FLOAT DEFAULT 1.0
);

-- Data Products table
CREATE TABLE data_products (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    study_id INTEGER REFERENCES clinical_study(id),
    type VARCHAR(100),
    format VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collections table
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collection Items table
CREATE TABLE collection_items (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER REFERENCES collections(id),
    data_product_id INTEGER REFERENCES data_products(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search History table
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    query VARCHAR NOT NULL,
    category VARCHAR,
    filters JSONB,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_saved BOOLEAN DEFAULT FALSE,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    use_count INTEGER DEFAULT 0
);

-- Add indexes for better query performance
CREATE INDEX idx_clinical_study_title ON clinical_study(title);
CREATE INDEX idx_clinical_study_status ON clinical_study(status);
CREATE INDEX idx_data_products_study_id ON data_products(study_id);
CREATE INDEX idx_collection_items_collection_id ON collection_items(collection_id);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
