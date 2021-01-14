import Draft from 'draft-js';

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
