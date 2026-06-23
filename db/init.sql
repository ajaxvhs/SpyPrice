-- 1. Core Product Table
CREATE TABLE IF NOT EXISTS product (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Marketplace Link Table
CREATE TABLE IF NOT EXISTS marketplace_link (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES product(id) ON DELETE CASCADE,
    marketplace VARCHAR(50) NOT NULL, -- e.g., 'Mercado Livre', 'Amazon'
    url TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Price History Table 
CREATE TABLE IF NOT EXISTS price_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    link_id UUID REFERENCES marketplace_link(id) ON DELETE CASCADE,
    price NUMERIC(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);