class RankingStore {
  constructor() {
    this.counts = {
      global: new Map(),
      python: new Map(),
      java: new Map(),
    };

    this.stats = {
      totalReposProcessed: 0,
      totalFilesProcessed: 0,
      totalFunctionsFound: 0,
      totalDistinctWords: 0,
      lastRepo: null,
      lastUpdate: null,
    };
  }

  static _toPositiveInt(value, fallback = 0) {
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0) {
      return fallback;
    }
    return Math.floor(n);
  }

  ingestEvent(payload) {
    const languageCounts = payload.language_counts || {};
    const pythonCounts = languageCounts.python || {};
    const javaCounts = languageCounts.java || {};

    this._accumulateIntoScope("python", pythonCounts);
    this._accumulateIntoScope("java", javaCounts);
    this._accumulateIntoScope("global", pythonCounts);
    this._accumulateIntoScope("global", javaCounts);

    this.stats.totalReposProcessed += 1;
    this.stats.totalFilesProcessed += RankingStore._toPositiveInt(payload.files_processed, 0);
    this.stats.totalFunctionsFound += RankingStore._toPositiveInt(payload.functions_found, 0);
    this.stats.totalDistinctWords = this.counts.global.size;
    this.stats.lastRepo = payload.repo || this.stats.lastRepo;
    this.stats.lastUpdate = new Date().toISOString();
  }

  _accumulateIntoScope(scope, countsObject) {
    const map = this.counts[scope];
    Object.entries(countsObject).forEach(([word, rawCount]) => {
      const count = RankingStore._toPositiveInt(rawCount, 0);
      if (!word || count <= 0) {
        return;
      }
      const current = map.get(word) || 0;
      map.set(word, current + count);
    });
  }

  getRanking(scope = "global", top = 10) {
    const selectedScope = ["global", "python", "java"].includes(scope) ? scope : "global";
    const limit = Math.max(1, Math.min(500, RankingStore._toPositiveInt(top, 10) || 10));

    return Array.from(this.counts[selectedScope].entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([word, count]) => ({ word, count }));
  }

  getStats() {
    return { ...this.stats };
  }

  snapshot(top = 10) {
    return {
      stats: this.getStats(),
      rankings: {
        global: this.getRanking("global", top),
        python: this.getRanking("python", top),
        java: this.getRanking("java", top),
      },
    };
  }
}

module.exports = { RankingStore };
