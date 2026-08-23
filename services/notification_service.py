"""Notification Engine for Expiry Alerts and Freshness Reminders."""
from typing import List, Dict, Any
from utils.database import get_db_connection
from services.kitchen_service import get_user_ingredients

def sync_inventory_notifications(user_id: int) -> int:
    """
    Scan user's actual inventory and generate notifications for items expiring today or soon.
    Only creates alerts for items the user actually owns.
    """
    if not user_id:
        return 0

    ingredients = get_user_ingredients(user_id)
    new_alerts_count = 0

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for item in ingredients:
            if item.days_remaining <= 0:
                title = f"Rescue Alert: {item.name}"
                msg = f"Your {item.name} ({item.quantity} {item.unit}) has reached its estimated shelf-life. We recommend cooking with it today!"
                alert_type = "USE TODAY"
            elif item.days_remaining <= 2:
                title = f"Freshness Notice: {item.name}"
                msg = f"Your {item.name} is approaching its estimated expiration in {item.days_remaining} day{'s' if item.days_remaining > 1 else ''}."
                alert_type = "USE SOON"
            else:
                continue

            # Check if an unread notification for this ingredient already exists to avoid spamming
            cursor.execute(
                """
                SELECT id FROM notifications
                WHERE user_id = ? AND ingredient_id = ? AND alert_type = ? AND is_read = 0;
                """,
                (user_id, item.id, alert_type)
            )
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO notifications (user_id, title, message, alert_type, ingredient_id, is_read)
                    VALUES (?, ?, ?, ?, ?, 0);
                    """,
                    (user_id, title, msg, alert_type, item.id)
                )
                new_alerts_count += 1

    return new_alerts_count

def get_user_notifications(user_id: int, unread_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve notifications strictly for the authenticated user."""
    if not user_id:
        return []

    # First sync
    sync_inventory_notifications(user_id)

    query = "SELECT * FROM notifications WHERE user_id = ?"
    params = [user_id]
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC;"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def mark_notification_read(user_id: int, notification_id: int) -> bool:
    """Mark a notification as read for user_id."""
    if not user_id or not notification_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?;",
            (notification_id, user_id)
        )
        return cursor.rowcount > 0

def clear_all_notifications(user_id: int) -> bool:
    """Mark all notifications as read for user_id."""
    if not user_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ?;",
            (user_id,)
        )
        return cursor.rowcount > 0
