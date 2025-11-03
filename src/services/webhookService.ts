import axios from 'axios';
import type { Logger } from 'winston';

// Base webhook payload structure
export interface WebhookPayload<T = any> {
  type: 'meeting_joined' | 'meeting_completed';
  sessionMeetingBotId: string;
  data: T;
}

// Data structure for meeting joined webhook
export interface MeetingJoinedData {
  correlationId: string;
  botId?: string;
  eventId?: string;
  provider?: 'google' | 'microsoft' | 'zoom';
}

// Data structure for meeting completed webhook
export interface MeetingCompletedData {
  uploadUrl: string;
  botId?: string;
  eventId?: string;
  provider?: 'google' | 'microsoft' | 'zoom';
}

// Parameters for joining notification
export interface MeetingJoinedParams {
  sessionMeetingBotId: string;
  correlationId: string;
  botId?: string;
  eventId?: string;
  provider?: 'google' | 'microsoft' | 'zoom';
}

// Parameters for completion notification
export interface MeetingCompletedParams {
  sessionMeetingBotId: string;
  uploadUrl: string;
  botId?: string;
  eventId?: string;
  provider?: 'google' | 'microsoft' | 'zoom';
}

export const notifyMeetingJoined = async (
  webhookUrl: string,
  params: MeetingJoinedParams,
  logger: Logger
): Promise<void> => {
  try {
    if (!webhookUrl) {
      logger.warn('No webhook URL provided, skipping meeting joined notification');
      return;
    }

    const payload: WebhookPayload<MeetingJoinedData> = {
      type: 'meeting_joined',
      sessionMeetingBotId: params.sessionMeetingBotId,
      data: {
        correlationId: params.correlationId,
        botId: params.botId,
        eventId: params.eventId,
        provider: params.provider,
      },
    };

    const response = await axios.post(webhookUrl, payload, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 second timeout
    });

    logger.info('Successfully notified webhook of meeting joined', {
      webhookUrl,
      sessionMeetingBotId: params.sessionMeetingBotId,
      correlationId: params.correlationId,
      botId: params.botId,
      eventId: params.eventId,
      provider: params.provider,
      responseStatus: response.status,
    });
  } catch (error) {
    logger.error('Failed to notify webhook of meeting joined', {
      webhookUrl,
      sessionMeetingBotId: params.sessionMeetingBotId,
      correlationId: params.correlationId,
      botId: params.botId,
      eventId: params.eventId,
      provider: params.provider,
      error: error instanceof Error ? error.message : String(error),
      axiosError: axios.isAxiosError(error) ? {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
      } : undefined,
    });
    throw error;
  }
};

export const notifyMeetingCompleted = async (
  webhookUrl: string,
  params: MeetingCompletedParams,
  logger: Logger
): Promise<void> => {
  try {
    if (!webhookUrl) {
      logger.warn('No webhook URL provided, skipping meeting completed notification');
      return;
    }

    const payload: WebhookPayload<MeetingCompletedData> = {
      type: 'meeting_completed',
      sessionMeetingBotId: params.sessionMeetingBotId,
      data: {
        uploadUrl: params.uploadUrl,
        botId: params.botId,
        eventId: params.eventId,
        provider: params.provider,
      },
    };

    const response = await axios.post(webhookUrl, payload, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 second timeout
    });

    logger.info('Successfully notified webhook of meeting completed', {
      webhookUrl,
      sessionMeetingBotId: params.sessionMeetingBotId,
      uploadUrl: params.uploadUrl,
      botId: params.botId,
      eventId: params.eventId,
      provider: params.provider,
      responseStatus: response.status,
    });
  } catch (error) {
    logger.error('Failed to notify webhook of meeting completed', {
      webhookUrl,
      sessionMeetingBotId: params.sessionMeetingBotId,
      uploadUrl: params.uploadUrl,
      botId: params.botId,
      eventId: params.eventId,
      provider: params.provider,
      error: error instanceof Error ? error.message : String(error),
      axiosError: axios.isAxiosError(error) ? {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
      } : undefined,
    });
    throw error;
  }
};