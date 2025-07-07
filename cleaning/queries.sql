
SELECT * FROM review
WHERE business_id NOT IN (
    SELECT business_id
    FROM business_categories
    WHERE category = 'Restaurants'
);

DELETE FROM review
WHERE business_id NOT IN (
    SELECT business_id
    FROM business_categories
    WHERE category = 'Restaurants'
);


DELETE FROM review WHERE business_id NOT IN(
SELECT business_id FROM business
WHERE business_id IN (
    SELECT business_id
    FROM business_categories
    WHERE category = 'Restaurants'
) AND review_count>=100);


ALTER TABLE review
ADD COLUMN review_int_id BIGINT AUTO_INCREMENT UNIQUE;

ALTER TABLE review_processed
ADD COLUMN review_int_id BIGINT UNIQUE;

INSERT INTO business_processed
SELECT *
FROM business
WHERE business_id IN (
    SELECT DISTINCT business_id FROM review_processed
);

INSERT INTO business_categories_processed
SELECT *
FROM business_categories
WHERE business_id IN (
    SELECT DISTINCT business_id FROM business_processed
);

INSERT INTO business_attributes_processed
SELECT *
FROM business_attributes
WHERE business_id IN (
    SELECT DISTINCT business_id FROM business_processed
);

INSERT INTO business_hours_processed
SELECT *
FROM  business_hours
WHERE business_id IN (
    SELECT DISTINCT business_id FROM business_processed
);
