import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

@Schema({ timestamps: { createdAt: 'created_at', updatedAt: false } })
export class Blog extends Document {
  id: string;
  @Prop({ required: true })
  title: string;

  @Prop({ required: true })
  content: string;

  @Prop({ required: true })
  url: string;

  @Prop({ type: [String], default: [] })
  tags: string[];

  @Prop()
  created_at: Date;
}

export const BlogSchema = SchemaFactory.createForClass(Blog);

// Add virtual 'id' to match Python backend behavior
BlogSchema.virtual('id').get(function () {
  return this._id.toHexString();
});
BlogSchema.set('toJSON', { virtuals: true });
BlogSchema.set('toObject', { virtuals: true });
