CREATE TABLE IF NOT EXISTS account (
    ID INT AUTO_INCREMENT NOT NULL,
    FName varchar(30) NOT NULL,
    LName varchar(30) NOT NULL,
    Email varchar(30) NOT NULL UNIQUE,
    Password char(64) NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS project (
    ID INT AUTO_INCREMENT NOT NULL,
    Name varchar(100) NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS sketcher (
    ID INT AUTO_INCREMENT NOT NULL,
    SketcherID INT NOT NULL,
    ProjectID INT NOT NULL,
    FOREIGN KEY (SketcherID) REFERENCES account(ID),
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT S_P_uniq UNIQUE (SketcherID, ProjectID)
);

CREATE TABLE IF NOT EXISTS manager (
    ID INT AUTO_INCREMENT NOT NULL,
    ManagerID INT NOT NULL,
    ProjectID INT NOT NULL,
    FOREIGN KEY (ManagerID) REFERENCES account(ID),
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT S_P_uniq UNIQUE (ManagerID, ProjectID)
);

CREATE TABLE IF NOT EXISTS composer (
    ID INT AUTO_INCREMENT NOT NULL,
    ComposerID INT NOT NULL,
    ProjectID INT NOT NULL,
    FOREIGN KEY (ComposerID) REFERENCES account(ID),
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT C_P_uniq UNIQUE (ComposerID, ProjectID)
);

CREATE TABLE IF NOT EXISTS writer (
    ID INT AUTO_INCREMENT NOT NULL,
    WriterID INT NOT NULL,
    ProjectID INT NOT NULL,
    FOREIGN KEY (WriterID) REFERENCES account(ID),
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT W_P_uniq UNIQUE (WriterID, ProjectID)
);

CREATE TABLE IF NOT EXISTS project_tag (
    ID INT AUTO_INCREMENT NOT NULL,
    Tag varchar(40) NOT NULL,
    ProjectID INT NOT NULL,
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT T_P_uniq UNIQUE (Tag, ProjectID)
);

CREATE TABLE IF NOT EXISTS season (
    ID INT AUTO_INCREMENT NOT NULL,
    SeasonNumber INT NOT NULL,
    Name varchar(80),
    Description TEXT,
    ProjectID INT NOT NULL,
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT SN_P_uniq UNIQUE (SeasonNumber, ProjectID)
);

CREATE TABLE IF NOT EXISTS episode (
    ID INT AUTO_INCREMENT NOT NULL,
    SeasonID INT NOT NULL,
    EpisodeNumber INT NOT NULL,
    Title varchar(80),
    Description TEXT,
    ProjectID INT NOT NULL,
    FOREIGN KEY (SeasonID) REFERENCES season(ID),
    FOREIGN KEY (ProjectID) REFERENCES project(ID),
    PRIMARY KEY (ID),
    CONSTRAINT SID_EN_P_uniq UNIQUE (SeasonID, EpisodeNumber, ProjectID)
);