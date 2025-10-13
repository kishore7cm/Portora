export const formatCurrency = (val: number, compact = false) => {
  if (val === undefined || val === null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: compact ? "compact" : "standard",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(val);
};

export const formatPercent = (val: number, showSign = true) => {
  if (val === undefined || val === null) return "—";
  const num = Number(val).toFixed(1);
  const prefix = showSign && val > 0 ? "+" : "";
  return `${prefix}${num}%`;
};

export const formatCount = (val: number) => {
  if (val === undefined || val === null) return "—";
  return val.toLocaleString("en-US");
};

export const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

export const formatNumber = (val: number, decimals = 0) => {
  if (val === undefined || val === null) return "—";
  return val.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};
