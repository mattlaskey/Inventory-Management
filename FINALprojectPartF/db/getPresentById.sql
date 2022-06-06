DELIMITER //
DROP PROCEDURE IF EXISTS getPresentById;

CREATE PROCEDURE getPresentById(IN pid INT)
BEGIN
    SELECT *
      FROM presents
        WHERE presentId = pid;

END //
DELIMITER ;