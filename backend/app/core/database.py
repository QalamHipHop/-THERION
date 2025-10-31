"""مدیریت اتصال به دیتابیس با AsyncIO"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from .config import settings

logger = logging.getLogger(__name__)

# ایجاد Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                        pool_pre_ping=True,
                            pool_recycle=3600,
                                poolclass=QueuePool,
                                )

                                # Session Factory
                                async_session_maker = async_sessionmaker(
                                    engine,
                                        class_=AsyncSession,
                                            expire_on_commit=False,
                                                autocommit=False,
                                                    autoflush=False,
                                                    )

                                                    # Base برای Models
                                                    Base = declarative_base()

                                                    # ================== Dependencies ==================
                                                    async def get_db() -> AsyncGenerator[AsyncSession, None]:
                                                        """دریافت database session برای FastAPI"""
                                                            async with async_session_maker() as session:
                                                                    try:
                                                                                yield session
                                                                                            await session.commit()
                                                                                                    except Exception as e:
                                                                                                                await session.rollback()
                                                                                                                            logger.error(f"Database error: {e}")
                                                                                                                                        raise
                                                                                                                                                finally:
                                                                                                                                                            await session.close()

                                                                                                                                                            # ================== Context Manager ==================
                                                                                                                                                            @asynccontextmanager
                                                                                                                                                            async def get_db_context():
                                                                                                                                                                """Context manager برای استفاده خارج از FastAPI"""
                                                                                                                                                                    async with async_session_maker() as session:
                                                                                                                                                                            try:
                                                                                                                                                                                        yield session
                                                                                                                                                                                                    await session.commit()
                                                                                                                                                                                                            except Exception as e:
                                                                                                                                                                                                                        await session.rollback()
                                                                                                                                                                                                                                    logger.error(f"Database context error: {e}")
                                                                                                                                                                                                                                                raise
                                                                                                                                                                                                                                                        finally:
                                                                                                                                                                                                                                                                    await session.close()

                                                                                                                                                                                                                                                                    # ================== Health Check ==================
                                                                                                                                                                                                                                                                    async def check_database_health() -> bool:
                                                                                                                                                                                                                                                                        """بررسی سلامت دیتابیس"""
                                                                                                                                                                                                                                                                            try:
                                                                                                                                                                                                                                                                                    async with get_db_context() as db:
                                                                                                                                                                                                                                                                                                await db.execute("SELECT 1")
                                                                                                                                                                                                                                                                                                        logger.info("Database health check: OK")
                                                                                                                                                                                                                                                                                                                return True
                                                                                                                                                                                                                                                                                                                    except Exception as e:
                                                                                                                                                                                                                                                                                                                            logger.error(f"Database health check failed: {e}")
                                                                                                                                                                                                                                                                                                                                    return False

                                                                                                                                                                                                                                                                                                                                    # ================== Initialize Database ==================
                                                                                                                                                                                                                                                                                                                                    async def init_db():
                                                                                                                                                                                                                                                                                                                                        """ایجاد جداول دیتابیس"""
                                                                                                                                                                                                                                                                                                                                            async with engine.begin() as conn:
                                                                                                                                                                                                                                                                                                                                                    await conn.run_sync(Base.metadata.create_all)
                                                                                                                                                                                                                                                                                                                                                        logger.info("Database tables created successfully")

                                                                                                                                                                                                                                                                                                                                                        # ================== Close Database ==================
                                                                                                                                                                                                                                                                                                                                                        async def close_db():
                                                                                                                                                                                                                                                                                                                                                            """بستن اتصالات دیتابیس"""
                                                                                                                                                                                                                                                                                                                                                                await engine.dispose()
                                                                                                                                                                                                                                                                                                                                                                    logger.info("Database connections closed")