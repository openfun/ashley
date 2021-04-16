import { createSpec, faker } from '@helpscout/helix';
import Draft from 'draft-js';
import { CommonDataProps } from '../../types/commonDataProps';

export const BlockMapFactory = (blocks: object[]) => {
  const defaultBlock = {
    key: Draft.genKey(),
    text: '',
    type: 'unstyled',
    depth: 0,
    inlineStyleRanges: [],
    entityRanges: [],
    data: {},
  };
  return JSON.stringify({
    blocks: blocks.map((block) => ({ ...defaultBlock, ...block })),
    entityMap: {},
  });
};

export const ContextFactory = (
  context: Partial<CommonDataProps['context']> = {},
) => {
  return createSpec({
    csrftoken: faker.random.alphaNumeric(64),
    ...context,
  });
};
