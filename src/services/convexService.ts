import { getConvexClient } from '../config/convex';
import { anyApi } from 'convex/server';
import type { Logger } from 'winston';

export interface UpdateSessionMeetingBotParams {
  status: string;
  botId?: string;
  eventId?: string;
}

export const updateSessionMeetingBot = async (
  params: UpdateSessionMeetingBotParams,
  logger: Logger
): Promise<void> => {
  try {
    const convex = getConvexClient();
    
    const result = await convex.mutation(
      anyApi.routes.sessions.sessionMeetingBots.mutations.unsafe_updateSessionMeetingBot,
      {
        id: params.botId,
        status: params.status,
      }
    );

    logger.info('Successfully updated session meeting bot', {
      botId: params.botId,
      status: params.status,
      eventId: params.eventId,
      result,
    });
  } catch (error) {
    logger.error('Failed to update session meeting bot', {
      botId: params.botId,
      status: params.status,
      eventId: params.eventId,
      error: error instanceof Error ? error.message : String(error),
    });
    throw error;
  }
};