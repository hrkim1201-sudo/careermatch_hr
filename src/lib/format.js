export function formatScore(score) {
  if (typeof score !== "number") return "-";
  return `${Math.round(score)}점`;
}

export function categoryLabel(category) {
  return category || "기타";
}

export function methodLabel(method) {
  switch (method) {
    case "openai": return "AI 의미 기반";
    case "tfidf": return "키워드 기반";
    case "template": return "템플릿 기반";
    default: return method || "기본";
  }
}

export function sourceLabel(source) {
  switch (source) {
    case "work24": return "고용24 실데이터";
    case "sample": return "샘플 데이터";
    case "empty": return "데이터 없음";
    default: return source || "-";
  }
}

export function relevanceLabel(relevance) {
  switch (relevance) {
    case "ncs_match": return "NCS 연계";
    case "keyword": return "키워드 연관";
    default: return "관련";
  }
}

export function formatExamDate(dateStr) {
  if (!dateStr || dateStr.length < 8) return dateStr || "-";
  return `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`;
}
