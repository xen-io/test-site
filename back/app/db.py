from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
from sqlalchemy import (Column, Integer, SmallInteger, String, Boolean,
                        UUID, DateTime, Date, ForeignKey, Text, JSON)


class Base(DeclarativeBase):
    pass


class SuperSubject(Base):
    __tablename__ = 'super_subject'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(100), nullable=False)

    subjects = relationship("Subject", back_populates="super_subject")
    competencies = relationship("Competency", back_populates="super_subject")


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    super_subject_id = Column(Integer, ForeignKey('super_subject.id'))
    first_name = Column(String(127), nullable=False)
    last_name = Column(String(127), nullable=False)
    middle_name = Column(String(127), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(127), nullable=False)

    is_admin = Column(Boolean, nullable=False, default=False)
    access_level = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    is_verified = Column(Boolean, nullable=False)

    # Relationships
    template_folders = relationship("TemplateFolder", back_populates="creator")
    pinned_folders = relationship("UserPinnedFolder", back_populates="user")
    user_areas = relationship("AuthUserArea", back_populates="user")
    user_schools = relationship("AuthUserSchool", back_populates="user")


class TemplateFolder(Base):
    __tablename__ = 'template_folders'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    creator_id = Column(UUID, ForeignKey('auth_user.id'), nullable=False)
    name = Column(String(63), nullable=False)
    permission_level = Column(SmallInteger, nullable=False)
    is_common = Column(Boolean, nullable=False)
    parent_folder_id = Column(UUID, ForeignKey('template_folders.id'))

    # Relationships
    creator = relationship("AuthUser", back_populates="template_folders")
    parent = relationship("TemplateFolder", remote_side=[id])
    children = relationship("TemplateFolder", back_populates="parent")
    templates = relationship("Template", back_populates="folder")
    pinned_folders = relationship("UserPinnedFolder", back_populates="folder")


class Template(Base):
    __tablename__ = 'templates'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    folder_id = Column(UUID, ForeignKey('template_folders.id'), nullable=False)
    name = Column(String(128), nullable=False)
    params = Column(JSON, nullable=False)
    permission_level = Column(SmallInteger, nullable=False)
    is_common = Column(Boolean, nullable=False)
    type = Column(SmallInteger, nullable=False, default=0)

    # Relationships
    folder = relationship("TemplateFolder", back_populates="templates")
    pinned_templates = relationship("UserPinnedTemplate", back_populates="template")


class UserPinnedFolder(Base):
    __tablename__ = 'user_pinned_folders'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    folder_id = Column(UUID, ForeignKey('template_folders.id'), nullable=False)
    user_id = Column(UUID, ForeignKey('auth_user.id'), nullable=False)
    is_pinned = Column(Boolean, nullable=False)

    # Relationships
    folder = relationship("TemplateFolder", back_populates="pinned_folders")
    user = relationship("AuthUser", back_populates="pinned_folders")
    pinned_templates = relationship("UserPinnedTemplate", back_populates="user_folder")


class UserPinnedTemplate(Base):
    __tablename__ = 'user_pinned_templates'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    user_folder_id = Column(UUID, ForeignKey('user_pinned_folders.id'), nullable=False)
    template_id = Column(UUID, ForeignKey('templates.id'), nullable=False)

    # Relationships
    user_folder = relationship("UserPinnedFolder", back_populates="pinned_templates")
    template = relationship("Template", back_populates="pinned_templates")


class Area(Base):
    __tablename__ = 'areas'

    code = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)

    # Relationships
    schools = relationship("School", back_populates="area")
    user_areas = relationship("AuthUserArea", back_populates="area")


class AuthUserArea(Base):
    __tablename__ = 'auth_user_areas'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    area_id = Column(Integer, ForeignKey('areas.code'), nullable=False)
    user_id = Column(UUID, ForeignKey('auth_user.id'), nullable=False)

    # Relationships
    area = relationship("Area", back_populates="user_areas")
    user = relationship("AuthUser", back_populates="user_areas")


class SchoolKind(Base):
    __tablename__ = 'school_kinds'

    code = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    # Relationships
    schools = relationship("School", back_populates="kind")


class SchoolProperty(Base):
    __tablename__ = 'school_properties'

    code = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Relationships
    schools = relationship("School", back_populates="property")


class TownType(Base):
    __tablename__ = 'town_types'

    code = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Relationships
    schools = relationship("School", back_populates="town_type")


class School(Base):
    __tablename__ = 'schools'

    code = Column(Integer, primary_key=True)
    vpr_code = Column(Integer)
    law_address = Column(String(150), nullable=False)
    short_name = Column(String(150), nullable=False)
    kind_code = Column(Integer, ForeignKey('school_kinds.code'), nullable=False)
    area_id = Column(Integer, ForeignKey('areas.code'), nullable=False)
    property_id = Column(Integer, ForeignKey('school_properties.code'), nullable=False)
    town_type_id = Column(Integer, ForeignKey('town_types.code'), nullable=False)

    # Relationships
    kind = relationship("SchoolKind", back_populates="schools")
    area = relationship("Area", back_populates="schools")
    property = relationship("SchoolProperty", back_populates="schools")
    town_type = relationship("TownType", back_populates="schools")
    user_schools = relationship("AuthUserSchool", back_populates="school")
    students = relationship("Student", back_populates="school")
    school_groups = relationship("SchoolGroupSchool", back_populates="school")


class AuthUserSchool(Base):
    __tablename__ = 'auth_user_school'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    school_id = Column(Integer, ForeignKey('schools.code'), nullable=False)
    user_id = Column(UUID, ForeignKey('auth_user.id'), nullable=False)

    # Relationships
    school = relationship("School", back_populates="user_schools")
    user = relationship("AuthUser", back_populates="user_schools")


class SchoolGroup(Base):
    __tablename__ = 'school_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    # Relationships
    schools = relationship("SchoolGroupSchool", back_populates="school_group")


class SchoolGroupSchool(Base):
    __tablename__ = 'school_groups_schools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey('schools.code'), nullable=False)
    school_group_id = Column(Integer, ForeignKey('school_groups.id'), nullable=False)

    # Relationships
    school = relationship("School", back_populates="school_groups")
    school_group = relationship("SchoolGroup", back_populates="schools")


class StudentCategory(Base):
    __tablename__ = 'student_categories'

    id = Column(Integer, primary_key=True)
    description = Column(String(127), nullable=False)

    # Relationships
    students = relationship("Student", back_populates="category")


class Student(Base):
    __tablename__ = 'students'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    base_code = Column(String(7), nullable=False)
    stud_code = Column(UUID, nullable=False)
    school_id = Column(Integer, ForeignKey('schools.code'), nullable=False)
    category_id = Column(Integer, ForeignKey('student_categories.id'), nullable=False)
    person_code = Column(Text)
    class_ = Column(String(5), nullable=False)
    is_ovz = Column(Boolean, nullable=False, default=False)
    is_medalist = Column(Boolean, nullable=False, default=False)
    is_admit = Column(Boolean, nullable=False, default=True)
    sex = Column(Boolean, nullable=False)

    # Relationships
    school = relationship("School", back_populates="students")
    category = relationship("StudentCategory", back_populates="students")
    planned_exams = relationship("PlannedExam", back_populates="student")
    exam_results = relationship("ExamResult", back_populates="student")


class ExamResultStatus(Base):
    __tablename__ = 'exam_result_status'

    id = Column(Integer, primary_key=True)
    description = Column(String(150), nullable=False)
    add_to_report = Column(Boolean, nullable=False, default=False)

    # Relationships
    exam_results = relationship("ExamResult", back_populates="status")


class Subject(Base):
    __tablename__ = 'subjects'

    code = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    super_subject_id = Column(SmallInteger, ForeignKey('super_subject.id'))

    # Relationships
    super_subject = relationship("SuperSubject", back_populates="subjects")
    test_schemes = relationship("TestScheme", back_populates="subject")


class ExamType(Base):
    __tablename__ = 'exam_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)

    # Relationships
    test_schemes = relationship("TestScheme", back_populates="exam_type")


class TestScheme(Base):
    __tablename__ = 'test_schemes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_type_id = Column(SmallInteger, ForeignKey('exam_types.id'), nullable=False)
    subject_id = Column(SmallInteger, ForeignKey('subjects.code'), nullable=False)
    exam_year = Column(SmallInteger, nullable=False)
    grade = Column(SmallInteger, nullable=False)

    # Relationships
    exam_type = relationship("ExamType", back_populates="test_schemes")
    subject = relationship("Subject", back_populates="test_schemes")
    planned_exams = relationship("PlannedExam", back_populates="schema")
    exam_results = relationship("ExamResult", back_populates="schema")
    work_plans = relationship("WorkPlan", back_populates="schema")


class PlannedExam(Base):
    __tablename__ = 'planned_exams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(UUID, ForeignKey('students.id'), nullable=False)
    schema_id = Column(Integer, ForeignKey('test_schemes.id'), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="planned_exams")
    schema = relationship("TestScheme", back_populates="planned_exams")


class ExamResult(Base):
    __tablename__ = 'exam_results'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    base_code = Column(String(7), nullable=False)
    exam_code = Column(UUID, nullable=False)
    first_points = Column(SmallInteger, nullable=False)
    final_points = Column(SmallInteger, nullable=False)
    completion_percents = Column(SmallInteger, nullable=False)
    score = Column(SmallInteger, nullable=False)
    student_id = Column(UUID, ForeignKey('students.id'), nullable=False)
    schema_id = Column(Integer, ForeignKey('test_schemes.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('exam_result_status.id'), nullable=False)
    auditorium = Column(String(4))
    exam_date = Column(Date, nullable=False)
    ppe_code = Column(String(6), nullable=False)
    variant = Column(Integer, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="exam_results")
    schema = relationship("TestScheme", back_populates="exam_results")
    status = relationship("ExamResultStatus", back_populates="exam_results")
    answers = relationship("Answer", back_populates="exam")


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    exam_id = Column(UUID, ForeignKey('exam_results.id'), nullable=False)
    current_point = Column(SmallInteger, nullable=False)
    task_number_in_part = Column(String(5), nullable=False)
    part = Column(SmallInteger, nullable=False)

    # Relationships
    exam = relationship("ExamResult", back_populates="answers")


class Competency(Base):
    __tablename__ = 'competencies'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    description = Column(Text, nullable=False)
    section_id = Column(Integer, ForeignKey('competencies.id'))
    super_subject_id = Column(SmallInteger, ForeignKey('super_subject.id'), nullable=False)
    skill = Column(Text)

    # Relationships
    section = relationship("Competency", remote_side=[id])
    super_subject = relationship("SuperSubject", back_populates="competencies")
    work_plan_competencies = relationship("WorkPlanCompetency", back_populates="competency")


class Difficulty(Base):
    __tablename__ = 'difficuelties'

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    # Relationships
    work_plans = relationship("WorkPlan", back_populates="difficulty")


class WorkPlan(Base):
    __tablename__ = 'work_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_id = Column(Integer, ForeignKey('test_schemes.id'), nullable=False)
    difficulty_id = Column(SmallInteger, ForeignKey('difficuelties.id'), nullable=False)
    task_number_in_part = Column(SmallInteger)
    part = Column(SmallInteger, nullable=False)
    task_number = Column(SmallInteger, nullable=False)
    criterion = Column(String(5))
    skill = Column(Text, nullable=False)
    max_points = Column(SmallInteger, nullable=False)

    # Relationships
    schema = relationship("TestScheme", back_populates="work_plans")
    difficulty = relationship("Difficulty", back_populates="work_plans")
    competencies = relationship("WorkPlanCompetency", back_populates="work_plan")


class WorkPlanCompetency(Base):
    __tablename__ = 'work_plans_competencies'

    id = Column(Integer, primary_key=True)
    work_plan_id = Column(Integer, ForeignKey('work_plans.id'), nullable=False)
    competencies_id = Column(Integer, ForeignKey('competencies.id'), nullable=False)

    # Relationships
    work_plan = relationship("WorkPlan", back_populates="competencies")
    competency = relationship("Competency", back_populates="work_plan_competencies")
