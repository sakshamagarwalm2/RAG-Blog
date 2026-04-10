import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Blog } from './schemas/blog.schema';

@Injectable()
export class BlogsService {
  constructor(@InjectModel(Blog.name) private blogModel: Model<Blog>) {}

  async findAll(): Promise<Blog[]> {
    return this.blogModel.find().sort({ created_at: -1 }).exec();
  }

  async findOne(id: string): Promise<Blog> {
    return this.blogModel.findById(id).exec();
  }

  async create(blogData: any): Promise<Blog> {
    const newBlog = new this.blogModel(blogData);
    return newBlog.save();
  }

  async delete(id: string): Promise<boolean> {
    const result = await this.blogModel.findByIdAndDelete(id).exec();
    return !!result;
  }

  async findIndexed(): Promise<Blog[]> {
    return this.blogModel.find({ indexed_at: { $ne: null } }).sort({ created_at: -1 }).exec();
  }

  async updateIndexedTimestamp(id: string, timestamp: Date | null): Promise<Blog> {
    return this.blogModel.findByIdAndUpdate(id, { indexed_at: timestamp }, { returnDocument: 'after' }).exec();
  }

  async findUnindexed(): Promise<Blog[]> {
    return this.blogModel.find({ indexed_at: null }).sort({ created_at: -1 }).exec();
  }

  async setAllBlogsIndexedTimestamp(timestamp: Date | null): Promise<any> {
    return this.blogModel.updateMany({}, { indexed_at: timestamp }).exec();
  }
}


