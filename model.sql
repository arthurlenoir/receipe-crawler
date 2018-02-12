CREATE TYPE meal_type AS ENUM ('appetizers', 'main-course', 'dessert', 'breakfast', 'drinks');
CREATE TYPE difficulty_type AS ENUM ('very easy', 'easy', 'medium', 'difficult');
CREATE TYPE cost_type AS ENUM ('cheap', 'average', 'expensive');


-- Amuse-bouche Full course dinner Hors d'oeuvre Dessert Entrée Entremet Main course Meal preparation Side dish

CREATE TABLE scraped_recipes (
    id serial PRIMARY KEY,
    url varchar(2000) UNIQUE NOT NULL,
    source varchar(50) NOT NULL,
    source_id varchar(50) NOT NULL,
    UNIQUE (source, source_id),

    title varchar(200) NOT NULL,
    raw_ingredients text[],
    raw_recipe text[],
    raw_difficulty varchar(200),
    raw_cost varchar(200),
    tags varchar(100)[],

    number smallint,
    unity_number varchar(200),

    type meal_type,
    difficulty difficulty_type,
    cost cost_type,
    preparation_time smallint, -- time in minutes
    cook_time smallint, -- time in minutes

    user_rating real,
    ratings_count integer,

    photos varchar(2000)[],

    ingredients json

);

-- Select every ingredient name
-- SELECT (o.ing->>'name'), (o.ing->>'uid'), COUNT(r.id) as count FROM scraped_recipes r, json_array_elements(r.ingredients) o(ing) GROUP BY (o.ing->>'name', o.ing->>'uid') ORDER BY count DESC LIMIT 1000;


CREATE TABLE ingredients (
    id serial PRIMARY KEY,
    foodb_id integer UNIQUE, 

    name varchar(255) NOT NULL,

    french_labels varchar(255)[],
    main_french_label varchar(255),

    vegan boolean DEFAULT FALSE,
    vegetarian boolean DEFAULT FALSE,
    gluten_free boolean DEFAULT FALSE

);