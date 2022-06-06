DELIMITER //
DROP PROCEDURE IF EXISTS getPresentsByUser;

CREATE PROCEDURE getPresentsByUser(IN uid INT)
BEGIN
    SELECT *
    FROM presents
    WHERE userId = uid;
END //
DELIMITER ;