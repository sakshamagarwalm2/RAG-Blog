import { Controller, Post, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiProperty } from '@nestjs/swagger';
import { ChatService } from './chat.service';

export class ChatMessageDto {
  @ApiProperty()
  role: string;
  @ApiProperty()
  content: string;
}

export class ChatRequestDto {
  @ApiProperty()
  query: string;
  @ApiProperty({ type: [ChatMessageDto], default: [] })
  chat_history: ChatMessageDto[];
}

@ApiTags('chat')
@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post()
  @ApiOperation({ summary: 'Send a chat message and get a RAG-based response' })
  async chat(@Body() payload: ChatRequestDto) {
    return this.chatService.answerQuery(payload.query, payload.chat_history);
  }
}
