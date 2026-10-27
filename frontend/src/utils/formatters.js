export const formatDate = (dateString) => {
  if (!dateString) return '—';
  try {
    const d = new Date(dateString);
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  } catch {
    return dateString;
  }
};

export const formatDuration = (seconds) => {
  if (seconds === undefined || seconds === null) return '—';
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  return `${Number(seconds).toFixed(2)}s`;
};

export const safeJsonStringify = (data) => {
  try {
    return JSON.stringify(data, null, 2);
  } catch {
    return String(data);
  }
};
