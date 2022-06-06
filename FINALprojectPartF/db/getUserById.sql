DELIMITER //
DROP PROCEDURE IF EXISTS getUserById;

CREATE PROCEDURE getUserById(IN uid INT)
BEGIN
    SELECT *
      FROM users
        WHERE userId = uid;

   IF (ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to find a valid user.';
        END IF;
END //