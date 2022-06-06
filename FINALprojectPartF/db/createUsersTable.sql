DELIMITER //
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userId    INT             NOT NULL AUTO_INCREMENT,
  userName  varchar(45)     NOT NULL,
  admin     BOOLEAN         NOT NULL,
  PRIMARY KEY (userID)
); //
DELIMITER ;