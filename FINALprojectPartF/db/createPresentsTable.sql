DELIMITER //
DROP TABLE IF EXISTS presents;
CREATE TABLE presents (
  presentId     INT             NOT NULL AUTO_INCREMENT,
  userId        INT             NOT NULL,
  presentName   varchar(45)     NOT NULL,
  presentDesc   varchar(255),
  presentPrice  DOUBLE           NOT NULL,
  PRIMARY KEY (presentID),
  FOREIGN KEY (userId) REFERENCES users (userId)
); //
DELIMITER ;