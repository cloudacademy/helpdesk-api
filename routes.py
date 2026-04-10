from flask import Blueprint, request, jsonify
from models import db, Ticket
from auth import require_bearer_token

bp = Blueprint("api", __name__, url_prefix="/api")

VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}

def _validate_ticket_payload(payload, partial=False):
    errors = []

    if not partial:
        if not payload.get("title"):
            errors.append("title is required")

    if "status" in payload:
        if payload["status"] not in VALID_STATUSES:
            errors.append(f"status must be one of {sorted(VALID_STATUSES)}")

    if "priority" in payload:
        if payload["priority"] not in VALID_PRIORITIES:
            errors.append(f"priority must be one of {sorted(VALID_PRIORITIES)}")

    return errors


@bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@bp.post("/tickets")
@require_bearer_token
def create_ticket():
    payload = request.get_json(silent=True) or {}
    errors = _validate_ticket_payload(payload, partial=False)
    if errors:
        return jsonify({"errors": errors}), 400

    ticket = Ticket(
        title=payload["title"],
        description=payload.get("description"),
        status=payload.get("status", "open"),
        priority=payload.get("priority", "medium"),
        requester_email=payload.get("requester_email"),
        assigned_to=payload.get("assigned_to"),
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201


@bp.get("/tickets")
@require_bearer_token
def list_tickets():
    # Basic filtering via query params
    status = request.args.get("status")
    priority = request.args.get("priority")

    q = Ticket.query
    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)

    tickets = q.order_by(Ticket.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tickets]), 200


@bp.get("/tickets/<int:ticket_id>")
@require_bearer_token
def get_ticket(ticket_id: int):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify(ticket.to_dict()), 200


@bp.put("/tickets/<int:ticket_id>")
@require_bearer_token
def replace_ticket(ticket_id: int):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    payload = request.get_json(silent=True) or {}
    errors = _validate_ticket_payload(payload, partial=False)
    if errors:
        return jsonify({"errors": errors}), 400

    ticket.title = payload["title"]
    ticket.description = payload.get("description")
    ticket.status = payload.get("status", ticket.status)
    ticket.priority = payload.get("priority", ticket.priority)
    ticket.requester_email = payload.get("requester_email")
    ticket.assigned_to = payload.get("assigned_to")

    db.session.commit()
    return jsonify(ticket.to_dict()), 200


@bp.patch("/tickets/<int:ticket_id>")
@require_bearer_token
def update_ticket(ticket_id: int):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    payload = request.get_json(silent=True) or {}
    errors = _validate_ticket_payload(payload, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400

    # Only update provided fields
    for field in ["title", "description", "status", "priority", "requester_email", "assigned_to"]:
        if field in payload:
            setattr(ticket, field, payload[field])

    db.session.commit()
    return jsonify(ticket.to_dict()), 200


@bp.delete("/tickets/<int:ticket_id>")
@require_bearer_token
def delete_ticket(ticket_id: int):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"deleted": True, "id": ticket_id}), 200
