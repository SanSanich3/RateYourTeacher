CREATE TABLE `Group`
(
  group_id             INT             NOT NULL
    PRIMARY KEY,
  group_full_name      TEXT            NOT NULL,
  group_end_of_lecture INT DEFAULT '0' NULL,
  CONSTRAINT Group_group_id_uindex
  UNIQUE (group_id)
)
  ENGINE = InnoDB;

CREATE TABLE Student
(
  student_id              INT AUTO_INCREMENT
    PRIMARY KEY,
  student_full_name       VARCHAR(100)      NOT NULL,
  student_avg_mark        FLOAT DEFAULT '0' NOT NULL,
  student_tg_username     VARCHAR(100)      NOT NULL,
  group_id                INT               NOT NULL,
  student_chat_id         INT DEFAULT '-1'  NOT NULL,
  student_vote_message_id INT DEFAULT '-1'  NULL,
  student_last_vote_id    INT DEFAULT '-1'  NULL,
  CONSTRAINT Student_student_id_uindex
  UNIQUE (student_id),
  CONSTRAINT Student_student_full_name_uindex
  UNIQUE (student_full_name),
  CONSTRAINT Student_student_tg_username_uindex
  UNIQUE (student_tg_username)
)
  ENGINE = InnoDB;

CREATE TABLE Teacher
(
  teacher_full_name  TEXT NULL,
  teacher_short_name TEXT NULL,
  teacher_id         INT  NOT NULL
    PRIMARY KEY,
  CONSTRAINT Teacher_teacher_id_uindex
  UNIQUE (teacher_id)
)
  ENGINE = InnoDB;

CREATE TABLE Vote
(
  vote_id                  INT AUTO_INCREMENT
    PRIMARY KEY,
  group_id                 INT             NOT NULL,
  teacher_id               INT             NOT NULL,
  vote_mark_sum            INT DEFAULT '0' NULL,
  vote_start_time          INT DEFAULT '0' NULL,
  vote_num_of_participants INT DEFAULT '0' NULL,
  CONSTRAINT Vote_vote_id_uindex
  UNIQUE (vote_id)
)
  ENGINE = InnoDB;


