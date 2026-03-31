import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

@Schema({ timestamps: { createdAt: 'created_at', updatedAt: false } })
export class Video extends Document {
  id: string;
  @Prop({ required: true })
  youtube_url: string;

  @Prop({ required: true, unique: true })
  video_id: string;

  @Prop({ required: true })
  title: string;

  @Prop({ required: true })
  channel: string;

  @Prop({ required: true })
  thumbnail_url: string;

  @Prop({ required: true })
  transcript_raw: string;

  @Prop({ required: true })
  transcript_word_count: number;

  @Prop({ required: true })
  summary: string;

  @Prop({ required: true })
  was_summarized: boolean;

  @Prop({ type: [String], default: [] })
  tags: string[];

  @Prop()
  created_at: Date;
}

export const VideoSchema = SchemaFactory.createForClass(Video);

VideoSchema.virtual('id').get(function () {
  return this._id.toHexString();
});
VideoSchema.set('toJSON', { virtuals: true });
VideoSchema.set('toObject', { virtuals: true });
