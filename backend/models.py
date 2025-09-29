# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class UserRole(str, enum.Enum):
    employee = "employee"
    admin = "admin"

class ReactionType(str, enum.Enum):
    like = "like"
    clap = "clap"
    star = "star"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    department = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.employee)
    joined_at = Column(DateTime, default=datetime.utcnow)

    shoutouts_sent = relationship("ShoutOut", back_populates="sender")
    comments = relationship("Comment", back_populates="user")
    reactions = relationship("Reaction", back_populates="user")
    reports = relationship("Report", back_populates="reporter")
    admin_logs = relationship("AdminLog", back_populates="admin")

class ShoutOut(Base):
    __tablename__ = "shoutouts"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", back_populates="shoutouts_sent")
    recipients = relationship("ShoutOutRecipient", back_populates="shoutout")
    comments = relationship("Comment", back_populates="shoutout")
    reactions = relationship("Reaction", back_populates="shoutout")
    reports = relationship("Report", back_populates="shoutout")

class ShoutOutRecipient(Base):
    __tablename__ = "shoutout_recipients"
    id = Column(Integer, primary_key=True, index=True)
    shoutout_id = Column(Integer, ForeignKey("shoutouts.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))

    shoutout = relationship("ShoutOut", back_populates="recipients")
    recipient = relationship("User")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    shoutout_id = Column(Integer, ForeignKey("shoutouts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    shoutout = relationship("ShoutOut", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True, index=True)
    shoutout_id = Column(Integer, ForeignKey("shoutouts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(ReactionType))

    shoutout = relationship("ShoutOut", back_populates="reactions")
    user = relationship("User", back_populates="reactions")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    shoutout_id = Column(Integer, ForeignKey("shoutouts.id"))
    reported_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    shoutout = relationship("ShoutOut", back_populates="reports")
    reporter = relationship("User", back_populates="reports")

class AdminLog(Base):
    __tablename__ = "admin_logs"
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(Text, nullable=False)
    target_id = Column(Integer)
    target_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    admin = relationship("User", back_populates="admin_logs")

