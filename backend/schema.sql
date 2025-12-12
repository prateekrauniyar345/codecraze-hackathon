-- ScholarSense Database Schema
-- PostgreSQL 14+

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS generated_materials CASCADE;
DROP TABLE IF EXISTS opportunity_requirements CASCADE;
DROP TABLE IF EXISTS opportunities CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
DROP TABLE IF EXISTS document_texts CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create enum types
CREATE TYPE document_type AS ENUM ('resume', 'cv', 'research_paper', 'project_information', 'cover_letter', 'other');
CREATE TYPE opportunity_status AS ENUM ('TO_APPLY', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED');
CREATE TYPE opportunity_type AS ENUM ('FULL_TIME', 'INTERNSHIP', 'RESEARCH');
CREATE TYPE material_type AS ENUM ('email', 'subject_line', 'sop_paragraph', 'fit_bullets');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size INTEGER,
    doc_type document_type DEFAULT 'resume',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Document Texts table (extracted text from documents)
CREATE TABLE document_texts (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    extracted_text TEXT NOT NULL,
    extraction_method VARCHAR(50) DEFAULT 'pypdf2',
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Profiles table (user's synthesized profile from resume)
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(50),
    linkedin_url VARCHAR(512),
    github_url VARCHAR(512),
    personal_website_url VARCHAR(512),
    summary TEXT,
    full_text TEXT NOT NULL,
    skills JSONB DEFAULT '[]',
    education JSONB DEFAULT '[]',
    experience JSONB DEFAULT '[]',
    projects JSONB DEFAULT '[]',
    languages JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    awards JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_profile_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Opportunities table
CREATE TABLE opportunities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(512) NOT NULL,
    organization VARCHAR(255),
    url TEXT,
    description TEXT NOT NULL,
    fit_score INTEGER CHECK (fit_score >= 0 AND fit_score <= 100),
    fit_analysis JSONB,
    status opportunity_status DEFAULT 'TO_APPLY',
    type opportunity_type DEFAULT 'FULL_TIME',
    deadline DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_opportunity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Opportunity Requirements table (parsed requirements from opportunity)
CREATE TABLE opportunity_requirements (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    requirement_text TEXT NOT NULL,
    requirement_type VARCHAR(100),
    is_mandatory BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_requirement_opportunity FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE
);

-- Generated Materials table
CREATE TABLE generated_materials (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    material_type material_type NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_material_opportunity FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    CONSTRAINT fk_material_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_document_texts_document_id ON document_texts(document_id);
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_opportunities_user_id ON opportunities(user_id);
CREATE INDEX idx_opportunities_status ON opportunities(status);
CREATE INDEX idx_opportunity_requirements_opportunity_id ON opportunity_requirements(opportunity_id);
CREATE INDEX idx_generated_materials_opportunity_id ON generated_materials(opportunity_id);
CREATE INDEX idx_generated_materials_user_id ON generated_materials(user_id);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opportunities_updated_at BEFORE UPDATE ON opportunities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE users IS 'User authentication and basic information';
COMMENT ON TABLE documents IS 'Uploaded resume/CV documents';
COMMENT ON TABLE document_texts IS 'Extracted text content from documents';
COMMENT ON TABLE profiles IS 'Parsed and structured user profile data';
COMMENT ON TABLE opportunities IS 'Job/internship/scholarship opportunities';
COMMENT ON TABLE opportunity_requirements IS 'Parsed requirements from opportunities';
COMMENT ON TABLE generated_materials IS 'AI-generated application materials';
