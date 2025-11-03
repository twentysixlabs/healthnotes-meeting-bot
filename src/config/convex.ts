import { ConvexHttpClient } from 'convex/browser';

let convexClient: ConvexHttpClient | null = null;

export const getConvexClient = (): ConvexHttpClient => {
  if (!convexClient) {
    const convexUrl = process.env.CONVEX_URL;
    
    if (!convexUrl) {
      throw new Error('CONVEX_URL environment variable is not set');
    }
    
    convexClient = new ConvexHttpClient(convexUrl);
  }
  
  return convexClient;
};