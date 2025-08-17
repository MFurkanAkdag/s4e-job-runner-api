#app/api/pagination.py

from __future__ import annotations

from typing import Any

from app.schemas.common import Pagination


def build_pagination(total: int, limit: int, offset: int) -> Pagination:
    return Pagination(limit=limit, offset=offset, total=total)


def paginate_query(query, limit: int, offset: int):
    return query.limit(limit).offset(offset)
