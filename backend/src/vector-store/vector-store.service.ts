import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';

export interface Metadata {
  source_type: 'blog' | 'video';
  source_id: string;
  title: string;
  url: string;
  chunk_text: string;
  chunk_index: number;
  thumbnail_url?: string;
  video_id?: string;
  channel?: string;
  score?: number;
  updated_at?: string;
}

@Injectable()
export class VectorStoreService implements OnModuleInit {
  private indexPath: string;
  private metadata: Metadata[] = [];
  private index: number[][] = [];

  constructor(private configService: ConfigService) {}

  onModuleInit() {
    this.indexPath = this.configService.get<string>('FAISS_INDEX_PATH', 'faiss_index');
    this.loadIndex();
  }

  private normalize(v: number[]): number[] {
    const norm = Math.sqrt(v.reduce((sum, val) => sum + val * val, 0));
    if (norm === 0) return v;
    return v.map((val) => val / norm);
  }

  private cosineSimilarity(v1: number[], v2: number[]): number {
    return v1.reduce((sum, val, i) => sum + val * v2[i], 0);
  }

  async buildIndex(
    items: { embedding: number[]; metadata: Metadata }[],
  ): Promise<{ total_chunks: number }> {
    if (!fs.existsSync(this.indexPath)) {
      fs.mkdirSync(this.indexPath, { recursive: true });
    }

    this.index = items.map((item) => this.normalize(item.embedding));
    this.metadata = items.map((item) => item.metadata);

    this.saveIndex();

    return { total_chunks: this.metadata.length };
  }

  async addToIndex(
    items: { embedding: number[]; metadata: Metadata }[],
  ): Promise<{ total_chunks: number }> {
    if (!fs.existsSync(this.indexPath)) {
      fs.mkdirSync(this.indexPath, { recursive: true });
    }

    // Load existing index if not already loaded
    if (this.index.length === 0) {
      this.loadIndex();
    }

    const newIndex = items.map((item) => this.normalize(item.embedding));
    const newMetadata = items.map((item) => item.metadata);

    this.index = [...this.index, ...newIndex];
    this.metadata = [...this.metadata, ...newMetadata];

    this.saveIndex();

    return { total_chunks: this.metadata.length };
  }

  async removeFromIndex(source_id: string): Promise<void> {
    if (this.index.length === 0) {
      this.loadIndex();
    }

    const indicesToKeep = this.metadata
      .map((m, i) => (m.source_id === source_id ? -1 : i))
      .filter((i) => i !== -1);

    if (indicesToKeep.length === this.metadata.length) return;

    this.index = indicesToKeep.map((i) => this.index[i]);
    this.metadata = indicesToKeep.map((i) => this.metadata[i]);

    this.saveIndex();
  }

  getIndexedIds(): string[] {
    if (this.index.length === 0) {
      this.loadIndex();
    }
    return Array.from(new Set(this.metadata.map((m) => m.source_id)));
  }

  getIndexedMetadataMap(): Record<string, { updated_at?: string }> {
    if (this.index.length === 0) {
      this.loadIndex();
    }
    const map: Record<string, { updated_at?: string }> = {};
    for (const m of this.metadata) {
      if (!map[m.source_id]) {
        map[m.source_id] = { updated_at: m.updated_at };
      }
    }
    return map;
  }

  private saveIndex() {
    const indexData = JSON.stringify(this.index);
    const metadataData = JSON.stringify(this.metadata);

    fs.writeFileSync(path.join(this.indexPath, 'index.json'), indexData);
    fs.writeFileSync(path.join(this.indexPath, 'metadata.json'), metadataData);
  }

  private loadIndex() {
    const indexFile = path.join(this.indexPath, 'index.json');
    const metadataFile = path.join(this.indexPath, 'metadata.json');

    if (fs.existsSync(indexFile) && fs.existsSync(metadataFile)) {
      this.index = JSON.parse(fs.readFileSync(indexFile, 'utf-8'));
      this.metadata = JSON.parse(fs.readFileSync(metadataFile, 'utf-8'));
    }
  }

  async search(queryVector: number[], k: number = 5): Promise<Metadata[]> {
    if (this.index.length === 0) return [];

    const normalizedQuery = this.normalize(queryVector);
    const scores = this.index.map((vector, i) => ({
      index: i,
      score: this.cosineSimilarity(normalizedQuery, vector),
    }));

    scores.sort((a, b) => b.score - a.score);

    return scores.slice(0, k).map((s) => ({
      ...this.metadata[s.index],
      score: s.score,
    }));
  }
}
