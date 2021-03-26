import { handle } from '../utils/errors/handle';
import { CommonDataProps } from '../types/commonDataProps';

export const appFrontendContext: CommonDataProps['context'] = (window as any)
  .__ashley_frontend_context__?.context;

if (!appFrontendContext) {
  handle(new Error('No frontend context available'));
}
