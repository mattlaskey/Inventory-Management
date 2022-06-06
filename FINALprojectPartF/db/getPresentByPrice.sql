DELIMITER //
DROP PROCEDURE IF EXISTS getPresentByPrice;

CREATE PROCEDURE getPresentByPrice(IN pPrice varchar(45))
BEGIN
    SELECT *
      FROM presents
        WHERE presentPrice = pPrice;
        
    IF (ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to find a present.';
        END IF;
END //
DELIMITER ;
