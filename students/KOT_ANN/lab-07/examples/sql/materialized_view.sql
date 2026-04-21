-- =====================================================
-- CQRS Read Model: Материализованное представление
-- для оптимизации запросов к ответам
-- =====================================================

-- 1. Создание материализованного представления
-- =====================================================

CREATE MATERIALIZED VIEW response_stats_mv AS
SELECT 
    r.form_id,
    f.form_title,
    COUNT(r.response_id) AS total_responses,
    COUNT(CASE WHEN r.is_suspect = false THEN 1 END) AS quality_responses,
    COUNT(CASE WHEN r.is_suspect = true THEN 1 END) AS suspect_responses,
    AVG(CASE WHEN r.quality_score IS NOT NULL THEN r.quality_score END) AS avg_quality_score,
    AVG(CASE WHEN r.rating IS NOT NULL THEN r.rating END) AS avg_rating,
    MIN(r.submitted_at) AS first_response,
    MAX(r.submitted_at) AS last_response
FROM responses r
LEFT JOIN forms f ON r.form_id = f.form_id
GROUP BY r.form_id, f.form_title;

-- 2. Индексы для материализованного представления
-- =====================================================

CREATE INDEX idx_response_stats_form_id ON response_stats_mv(form_id);
CREATE INDEX idx_response_stats_quality ON response_stats_mv(quality_responses DESC);
CREATE INDEX idx_response_stats_avg_rating ON response_stats_mv(avg_rating DESC);

-- 3. Функция обновления материализованного представления
-- =====================================================

CREATE OR REPLACE FUNCTION refresh_response_stats()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY response_stats_mv;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 4. Триггер для автоматического обновления при изменении данных
-- =====================================================

CREATE TRIGGER trigger_refresh_response_stats
AFTER INSERT OR UPDATE ON responses
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_response_stats();

-- 5. Read Model таблица для денормализованных ответов
-- =====================================================

CREATE TABLE response_views (
    response_id VARCHAR(64) PRIMARY KEY,
    form_id VARCHAR(64) NOT NULL,
    form_title VARCHAR(255),
    answers JSONB NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    started_at TIMESTAMP NOT NULL,
    submitted_at TIMESTAMP NOT NULL,
    filling_time_sec INTEGER NOT NULL,
    ip_address VARCHAR(45),
    country VARCHAR(100),
    city VARCHAR(100),
    device_type VARCHAR(50),
    is_suspect BOOLEAN NOT NULL DEFAULT FALSE,
    quality_score FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- 6. Индексы для response_views
-- =====================================================

CREATE INDEX idx_response_views_form_id ON response_views(form_id);
CREATE INDEX idx_response_views_form_submitted ON response_views(form_id, submitted_at DESC);
CREATE INDEX idx_response_views_rating ON response_views(form_id, rating);
CREATE INDEX idx_response_views_suspect ON response_views(form_id, is_suspect);
CREATE INDEX idx_response_views_quality ON response_views(quality_score DESC);

-- 7. Оптимизированные запросы
-- =====================================================

-- 7.1. Получить топ-10 форм по среднему рейтингу
EXPLAIN ANALYZE
SELECT form_id, form_title, avg_rating, total_responses
FROM response_stats_mv
WHERE total_responses > 10
ORDER BY avg_rating DESC
LIMIT 10;

-- 7.2. Получить ответы с низкой оценкой (для уведомлений)
EXPLAIN ANALYZE
SELECT response_id, form_id, rating, comment, submitted_at
FROM response_views
WHERE rating <= 2
ORDER BY submitted_at DESC;

-- 7.3. Получить статистику по форме за период
EXPLAIN ANALYZE
SELECT 
    DATE(submitted_at) AS day,
    COUNT(*) AS total,
    AVG(quality_score) AS avg_quality
FROM response_views
WHERE form_id = 'FORM-42'
    AND submitted_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(submitted_at)
ORDER BY day DESC;

-- 8. Очистка старых данных (партиционирование)
-- =====================================================

-- Создание партиционированной таблицы для старых ответов
CREATE TABLE response_views_archive PARTITION OF response_views
FOR VALUES FROM (MINVALUE) TO ('2024-01-01');

-- Автоматическое удаление старых записей (через 90 дней)
CREATE OR REPLACE FUNCTION archive_old_responses()
RETURNS void AS $$
BEGIN
    DELETE FROM response_views
    WHERE submitted_at < NOW() - INTERVAL '90 days';
    
    REFRESH MATERIALIZED VIEW CONCURRENTLY response_stats_mv;
END;
$$ LANGUAGE plpgsql;

-- 9. Просмотр плана выполнения запроса
-- =====================================================

-- Получить план запроса для статистики
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT form_id, COUNT(*), AVG(quality_score)
FROM response_views
WHERE submitted_at >= NOW() - INTERVAL '7 days'
GROUP BY form_id;