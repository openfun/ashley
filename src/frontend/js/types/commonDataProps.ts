export interface CommonDataProps {
  context: {
    csrftoken: string;
    max_upload: number;
    image_type: string[];
  };
}
