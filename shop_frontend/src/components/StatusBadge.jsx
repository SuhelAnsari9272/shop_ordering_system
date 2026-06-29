const STATUS_LABELS = {
  RECEIVED:  { label: 'Received',  cls: 'badge-received'  },
  PREPARING: { label: 'Preparing', cls: 'badge-preparing' },
  READY:     { label: 'Ready',     cls: 'badge-ready'     },
  COMPLETED: { label: 'Completed', cls: 'badge-completed' },
  CANCELLED: { label: 'Cancelled', cls: 'badge-cancelled' },
}

export default function StatusBadge({ status }) {
  const cfg = STATUS_LABELS[status] || { label: status, cls: '' }
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
}
