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

  async getCount(): Promise<number> {
    return this.blogModel.countDocuments().exec();
  }
}
