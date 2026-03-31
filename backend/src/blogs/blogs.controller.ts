import { Controller, Get, Post, Delete, Param, Body, HttpException, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiProperty } from '@nestjs/swagger';
import { BlogsService } from './blogs.service';

export class BlogCreateDto {
  @ApiProperty()
  title: string;
  @ApiProperty()
  content: string;
  @ApiProperty()
  url: string;
  @ApiProperty({ required: false })
  tags?: string[];
}

@ApiTags('blogs')
@Controller('blogs')
export class BlogsController {
  constructor(private readonly blogsService: BlogsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all blogs' })
  async getBlogs() {
    return this.blogsService.findAll();
  }

  @Post()
  @ApiOperation({ summary: 'Add a new blog' })
  async addBlog(@Body() blogData: BlogCreateDto) {
    try {
      return await this.blogsService.create(blogData);
    } catch (error) {
      throw new HttpException('Failed to create blog', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a blog' })
  async deleteBlog(@Param('id') id: string) {
    const deleted = await this.blogsService.delete(id);
    if (!deleted) {
      throw new HttpException('Blog not found', HttpStatus.NOT_FOUND);
    }
    return { deleted: true };
  }
}
