import re
from dataclasses import dataclass


DEFAULT_SESSION_ID = "default"


@dataclass
class ContextState:
    label: str
    description: str
    source_question: str

    def to_prompt_text(self):
        return (
            f"Current context: {self.label}\n"
            f"Meaning: {self.description}\n"
            f"Context was set by this earlier user question: "
            f"{self.source_question}"
        )

    def to_response_dict(self):
        return {
            "label": self.label,
            "description": self.description,
            "source_question": self.source_question
        }


_SESSION_CONTEXTS = {}


_AMBIGUOUS_FOLLOW_UP_PATTERNS = [
    r"\baverages?\b",
    r"\bavg\b",
    r"\bhighest\b",
    r"\blowest\b",
    r"\bmaximum\b",
    r"\bminimum\b",
    r"\bmax\b",
    r"\bmin\b",
    r"\btotal\b",
    r"\bsum\b",
    r"\bvalues?\b",
    r"\bdetails?\b",
    r"\brecords?\b",
    r"\bshow\s+all\b"
]


_CONTEXT_DEFINITIONS = [
    {
        "label": "order_items",
        "patterns": [
            r"\border\s+items?\b",
            r"\bitems?\b",
            r"\bsellers?\b",
            r"\bshipping\b",
            r"\bshipping\s+charges?\b",
            r"\bprices?\b"
        ],
        "description": (
            "line-item order details from order_items. Use price for item "
            "value and shipping_charges for shipping cost."
        )
    },
    {
        "label": "orders",
        "patterns": [
            r"\borders?\b",
            r"\border\s+status\b",
            r"\bdeliver(?:y|ed)?\b",
            r"\bapproved?\b"
        ],
        "description": (
            "order records from orders. Use orders for order status, "
            "purchase timestamps, approval timestamps, and delivery dates. "
            "If monetary order value is requested, join payments by order_id "
            "and use payment_value."
        )
    },
    {
        "label": "payments",
        "patterns": [
            r"\bpayments?\b",
            r"\bpaid\b",
            r"\bpayment\s+types?\b",
            r"\binstallments?\b"
        ],
        "description": (
            "payment records from payments. Use payment_value for monetary "
            "value, payment_type for method, and payment_installments for "
            "installment count."
        )
    },
    {
        "label": "products",
        "patterns": [
            r"\bproducts?\b",
            r"\bproduct\s+categor(?:y|ies)\b",
            r"\bcategor(?:y|ies)\b",
            r"\bweights?\b",
            r"\bdimensions?\b"
        ],
        "description": (
            "product catalog details from products, including category, "
            "weight, and package dimensions."
        )
    },
    {
        "label": "customers",
        "patterns": [
            r"\bcustomers?\b",
            r"\bcustomer\s+cities?\b",
            r"\bcities?\b",
            r"\bstates?\b",
            r"\bzip\b",
            r"\bpincode\b"
        ],
        "description": (
            "customer location details from customers, including city, "
            "state, and zip code prefix."
        )
    },
    {
        "label": "purchase",
        "patterns": [
            r"\bpurchases?\b",
            r"\bpurchased?\b",
            r"\bbuy\b",
            r"\bbought\b",
            r"\bsales?\b"
        ],
        "description": (
            "purchase transactions across orders and payments. Use orders "
            "for purchase timestamps/status and payments.payment_value for "
            "purchase value."
        )
    }
]


def normalize_session_id(session_id):
    if not session_id:
        return DEFAULT_SESSION_ID

    normalized = str(session_id).strip()

    return normalized or DEFAULT_SESSION_ID


def _detect_explicit_context(user_query):
    query = user_query.lower()

    for definition in _CONTEXT_DEFINITIONS:
        for pattern in definition["patterns"]:
            if re.search(pattern, query):
                return ContextState(
                    label=definition["label"],
                    description=definition["description"],
                    source_question=user_query
                )

    return None


def needs_context_clarification(user_query):
    if _detect_explicit_context(user_query):
        return False

    query = user_query.lower()

    return any(
        re.search(pattern, query)
        for pattern in _AMBIGUOUS_FOLLOW_UP_PATTERNS
    )


def _get_definition(label):
    for definition in _CONTEXT_DEFINITIONS:
        if definition["label"] == label:
            return definition

    return None


def _load_saved_context(session_id):
    from modules.chat_history import get_latest_session_context

    saved_context = get_latest_session_context(session_id)

    if not saved_context:
        return None

    label, source_question = saved_context
    definition = _get_definition(label)

    if not definition:
        return None

    return ContextState(
        label=label,
        description=definition["description"],
        source_question=source_question
    )


def resolve_session_context(user_query, session_id):
    normalized_session_id = normalize_session_id(session_id)
    explicit_context = _detect_explicit_context(user_query)

    if explicit_context:
        _SESSION_CONTEXTS[normalized_session_id] = explicit_context

        return normalized_session_id, explicit_context, True

    session_context = _SESSION_CONTEXTS.get(normalized_session_id)

    if not session_context:
        session_context = _load_saved_context(normalized_session_id)

        if session_context:
            _SESSION_CONTEXTS[normalized_session_id] = session_context

    return normalized_session_id, session_context, False
