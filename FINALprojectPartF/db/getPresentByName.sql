DELIMITER //
DROP PROCEDURE IF EXISTS getPresentByName;

CREATE PROCEDURE getPresentByName(IN pName varchar(45))
BEGIN
    SELECT *
      FROM presents
        WHERE PresentName = pName;
        
    IF (ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to find present.';
        END IF;
END //
DELIMITER ;
