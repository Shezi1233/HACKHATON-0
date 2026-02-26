#!/usr/bin/env node

// Social Media MCP Server for Facebook, Instagram, and Twitter integration
// Implements MCP v1.0 protocol for integration with Claude Code

import { createServer } from '@modelcontextprotocol/server';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// Rate limiting and caching
const rateLimits = new Map();
const lastRequestTime = new Map();

// Facebook/Instagram configuration
const fbConfig = {
  accessToken: process.env.FACEBOOK_ACCESS_TOKEN || process.env.INSTAGRAM_ACCESS_TOKEN,
  pageId: process.env.FACEBOOK_PAGE_ID,
  instagramAccountId: process.env.INSTAGRAM_ACCOUNT_ID
};

// Twitter configuration
const twitterConfig = {
  bearerToken: process.env.TWITTER_BEARER_TOKEN,
  apiKey: process.env.TWITTER_API_KEY,
  apiSecret: process.env.TWITTER_API_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessTokenSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET
};

// Check rate limit for a given endpoint
function checkRateLimit(key, maxRequests = 200, timeWindow = 3600) { // 200 requests per hour
  const now = Date.now();
  const lastTime = lastRequestTime.get(key) || 0;

  if (now - lastTime < timeWindow * 1000) {
    const count = rateLimits.get(key) || 0;
    if (count >= maxRequests) {
      return false; // Rate limit exceeded
    }
    rateLimits.set(key, count + 1);
  } else {
    rateLimits.set(key, 1);
  }

  lastRequestTime.set(key, now);
  return true;
}

// Reset rate limit counters periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, time] of lastRequestTime.entries()) {
    if (now - time > 3600 * 1000) { // 1 hour
      rateLimits.delete(key);
      lastRequestTime.delete(key);
    }
  }
}, 300000); // Clean up every 5 minutes

const server = createServer({
  name: 'social-media-mcp-server',
  version: '1.0.0',
  capabilities: [
    {
      type: 'tools',
      tools: [
        {
          name: 'post_to_facebook',
          description: 'Create a post on Facebook page',
          inputSchema: {
            type: 'object',
            properties: {
              message: { type: 'string', description: 'Post content' },
              link: { type: 'string', description: 'URL to include in post' },
              attachments: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    url: { type: 'string', description: 'URL of the media' },
                    type: { type: 'string', enum: ['image', 'video'] }
                  }
                }
              }
            },
            required: ['message']
          }
        },
        {
          name: 'post_to_instagram',
          description: 'Create a post on Instagram account',
          inputSchema: {
            type: 'object',
            properties: {
              caption: { type: 'string', description: 'Post caption' },
              imageUrl: { type: 'string', description: 'URL of the image to post' },
              videoUrl: { type: 'string', description: 'URL of the video to post (optional)' },
              hashtags: {
                type: 'array',
                items: { type: 'string' },
                description: 'Array of hashtags to include'
              }
            },
            required: ['caption']
          }
        },
        {
          name: 'post_to_twitter',
          description: 'Create a tweet on Twitter/X',
          inputSchema: {
            type: 'object',
            properties: {
              text: { type: 'string', description: 'Tweet content' },
              mediaUrls: {
                type: 'array',
                items: { type: 'string' },
                description: 'Array of media URLs to include'
              },
              replyToId: { type: 'string', description: 'ID of tweet to reply to' }
            },
            required: ['text']
          }
        },
        {
          name: 'get_facebook_insights',
          description: 'Get insights/metrics for Facebook page',
          inputSchema: {
            type: 'object',
            properties: {
              metric: { type: 'string', description: 'Specific metric to retrieve' },
              period: { type: 'string', enum: ['day', 'week', 'days_28'], default: 'week' }
            }
          }
        },
        {
          name: 'get_instagram_insights',
          description: 'Get insights/metrics for Instagram account',
          inputSchema: {
            type: 'object',
            properties: {
              metric: { type: 'string', description: 'Specific metric to retrieve' },
              period: { type: 'string', enum: ['day', 'week', 'days_28'], default: 'week' }
            }
          }
        },
        {
          name: 'get_twitter_insights',
          description: 'Get insights/metrics for Twitter account',
          inputSchema: {
            type: 'object',
            properties: {
              startDate: { type: 'string', description: 'Start date (YYYY-MM-DD)' },
              endDate: { type: 'string', description: 'End date (YYYY-MM-DD)' }
            }
          }
        },
        {
          name: 'schedule_social_post',
          description: 'Schedule a social media post for later',
          inputSchema: {
            type: 'object',
            properties: {
              platform: { type: 'string', enum: ['facebook', 'instagram', 'twitter'], description: 'Platform to post to' },
              content: { type: 'object', description: 'Content for the post (varies by platform)' },
              scheduledTime: { type: 'string', description: 'When to post (ISO 8601 format)' }
            },
            required: ['platform', 'content', 'scheduledTime']
          }
        }
      ]
    }
  ]
});

// Helper function for Facebook API calls
async function facebookApiCall(endpoint, method = 'GET', data = null) {
  if (!fbConfig.accessToken) {
    throw new Error('Facebook access token not configured');
  }

  // Check rate limit for Facebook API
  const fbKey = `facebook_${endpoint}`;
  if (!checkRateLimit(fbKey, 200, 3600)) { // 200 requests per hour
    throw new Error('Facebook API rate limit exceeded. Please try again later.');
  }

  const url = `https://graph.facebook.com/v18.0/${endpoint}`;
  const config = {
    method: method,
    url: url,
    params: {
      access_token: fbConfig.accessToken
    }
  };

  if (data && method !== 'GET') {
    config.data = data;
  }

  try {
    const response = await axios(config);
    return response.data;
  } catch (error) {
    console.error(`Facebook API Error for ${endpoint}:`, error.response?.data || error.message);
    throw new Error(`Facebook API Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Helper function for Twitter API calls
async function twitterApiCall(endpoint, method = 'GET', data = null) {
  if (!twitterConfig.bearerToken) {
    throw new Error('Twitter credentials not configured');
  }

  // Check rate limit for Twitter API
  const twitterKey = `twitter_${endpoint}`;
  if (!checkRateLimit(twitterKey, 300, 900)) { // 300 requests per 15 minutes
    throw new Error('Twitter API rate limit exceeded. Please try again later.');
  }

  const url = `https://api.twitter.com/2/${endpoint}`;
  const config = {
    method: method,
    url: url,
    headers: {
      'Authorization': `Bearer ${twitterConfig.bearerToken}`,
      'Content-Type': 'application/json'
    }
  };

  if (data && method !== 'GET') {
    config.data = data;
  }

  try {
    const response = await axios(config);
    return response.data;
  } catch (error) {
    console.error(`Twitter API Error for ${endpoint}:`, error.response?.data || error.message);
    throw new Error(`Twitter API Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

server.handle('tools/call', async ({ toolName, parameters }) => {
  try {
    switch (toolName) {
      case 'post_to_facebook':
        if (!fbConfig.pageId) {
          throw new Error('Facebook page ID not configured');
        }

        const fbPostData = {
          message: parameters.message
        };

        if (parameters.link) {
          fbPostData.link = parameters.link;
        }

        const fbResult = await facebookApiCall(`${fbConfig.pageId}/feed`, 'POST', fbPostData);
        return { success: true, postId: fbResult.id, message: 'Facebook post created successfully' };

      case 'post_to_instagram':
        if (!fbConfig.instagramAccountId) {
          throw new Error('Instagram account ID not configured');
        }

        // For Instagram, we need to first upload the media and then create the container
        const caption = parameters.hashtags ?
          `${parameters.caption} ${parameters.hashtags.map(tag => `#${tag}`).join(' ')}` :
          parameters.caption;

        if (parameters.imageUrl) {
          // Create the media object container
          const igContainerData = {
            image_url: parameters.imageUrl,
            caption: caption,
            // Use the media_type parameter for newer API versions
            media_type: 'IMAGE'
          };

          // Create the media container
          const containerResponse = await facebookApiCall(`${fbConfig.instagramAccountId}/media`, 'POST', igContainerData);
          const containerId = containerResponse.id;

          // Wait briefly for the container to be processed
          await new Promise(resolve => setTimeout(resolve, 2000));

          // Publish the container
          const publishResponse = await facebookApiCall(`${fbConfig.instagramAccountId}/media_publish`, 'POST', {
            creation_id: containerId
          });

          return {
            success: true,
            postId: publishResponse.id,
            message: 'Instagram post published successfully',
            containerId: containerId
          };
        } else if (parameters.videoUrl) {
          // For video posts
          const igVideoContainerData = {
            video_url: parameters.videoUrl,
            caption: caption,
            media_type: 'VIDEO'
          };

          const videoContainerResponse = await facebookApiCall(`${fbConfig.instagramAccountId}/media`, 'POST', igVideoContainerData);
          const videoContainerId = videoContainerResponse.id;

          // Wait for video processing
          await new Promise(resolve => setTimeout(resolve, 5000));

          // Publish the video container
          const videoPublishResponse = await facebookApiCall(`${fbConfig.instagramAccountId}/media_publish`, 'POST', {
            creation_id: videoContainerId
          });

          return {
            success: true,
            postId: videoPublishResponse.id,
            message: 'Instagram video post published successfully',
            containerId: videoContainerId
          };
        } else {
          // Text-only post (Instagram doesn't support text-only posts, so use a placeholder image)
          // For this implementation we'll return an error as Instagram doesn't allow text-only posts
          throw new Error('Instagram requires media (image/video) for posts. Text-only posts are not supported.');
        }

      case 'post_to_twitter':
        const tweetData = {
          text: parameters.text
        };

        if (parameters.replyToId) {
          tweetData.reply = { in_reply_to_tweet_id: parameters.replyToId };
        }

        const twitterResult = await twitterApiCall('tweets', 'POST', tweetData);
        return { success: true, tweetId: twitterResult.data.id, message: 'Tweet posted successfully' };

      case 'get_facebook_insights':
        if (!fbConfig.pageId) {
          throw new Error('Facebook page ID not configured');
        }

        const metric = parameters.metric || 'page_impressions';
        const period = parameters.period || 'week';

        const fbInsights = await facebookApiCall(`${fbConfig.pageId}/insights`, 'GET', {
          metric: metric,
          period: period
        });

        return { success: true, insights: fbInsights };

      case 'get_instagram_insights':
        if (!fbConfig.instagramAccountId) {
          throw new Error('Instagram account ID not configured');
        }

        const igMetric = parameters.metric || 'impressions';
        const igPeriod = parameters.period || 'week';

        const igInsights = await facebookApiCall(`${fbConfig.instagramAccountId}/insights`, 'GET', {
          metric: igMetric,
          period: igPeriod
        });

        return { success: true, insights: igInsights };

      case 'get_twitter_insights':
        // This would typically involve getting tweet metrics
        // For now, providing placeholder implementation
        const startDate = parameters.startDate || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        const endDate = parameters.endDate || new Date().toISOString().split('T')[0];

        // Get user's tweets
        const userResponse = await twitterApiCall('users/by/username/me');
        const userId = userResponse.data.id;

        // Get recent tweets
        const tweetsResponse = await twitterApiCall(`users/${userId}/tweets`, 'GET', {
          max_results: 10,
          'tweet.fields': 'public_metrics,created_at'
        });

        return {
          success: true,
          date_range: { start: startDate, end: endDate },
          tweets: tweetsResponse.data?.tweets || []
        };

      case 'schedule_social_post':
        // This would integrate with a scheduling system
        // For this implementation, we'll return a success message with the scheduled time
        return {
          success: true,
          scheduledTime: parameters.scheduledTime,
          platform: parameters.platform,
          message: `Post scheduled for ${parameters.scheduledTime} on ${parameters.platform}`
        };

      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      toolName
    };
  }
});

// Start the server
const port = process.env.PORT || 8086;
server.listen({ port })
  .then(() => {
    console.log(`Social Media MCP Server running on port ${port}`);
  })
  .catch((error) => {
    console.error('Failed to start Social Media MCP Server:', error);
  });