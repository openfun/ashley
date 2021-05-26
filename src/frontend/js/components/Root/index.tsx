import { get, includes, startCase } from 'lodash-es';

import React from 'react';
import ReactDOM from 'react-dom';
import { DashboardModerators } from '../DashboardModerators';
import { AshleyEditor } from '../AshleyEditor';

// List the top-level components that can be directly called from the Django templates in an interface
// for type-safety when we call them. This will let us use the props for any top-level component in a
// way TypeScript understand and accepts
interface ComponentLibrary {
  DashboardModerators: typeof DashboardModerators;
  AshleyEditor: typeof AshleyEditor;
}
// Actually create the component map that we'll use below to access our component classes
const componentLibrary: ComponentLibrary = {
  DashboardModerators,
  AshleyEditor,
};
// Type guard: ensures a given string (candidate) is indeed a proper key of the componentLibrary with a corresponding
// component. This is a runtime check but it allows TS to check the component prop types at compile time
function isComponentName(
  candidate: keyof ComponentLibrary | string,
): candidate is keyof ComponentLibrary {
  return includes(Object.keys(componentLibrary), candidate);
}

interface RootProps {
  ashleyReactSpots: Element[];
}

export const Root = ({ ashleyReactSpots }: RootProps) => {
  const portals = ashleyReactSpots.map((element: Element) => {
    // Generate a component name. It should be a key of the componentLibrary object / ComponentLibrary interface
    const componentName = startCase(
      get(element.className.match(/ashley-react--([a-zA-Z-]*)/), '[1]') || '',
    )
      .split(' ')
      .join('');
    // Sanity check: only attempt to access and render components for which we do have a valid name
    if (isComponentName(componentName)) {
      // Do get the component dynamically. We know this WILL produce a valid component thanks to the type guard
      const Component = componentLibrary[componentName];

      let props: any = {};

      // Get the incoming props to pass our component from `data-props` if applicable
      const dataProps = element.getAttribute('data-props');
      if (dataProps) {
        props = { ...props, ...JSON.parse(dataProps) };
      }

      return ReactDOM.createPortal(<Component {...props} />, element);
    } else {
      // Through a warning at runtime when we fail to find a matching component
      console.warn(
        'Failed to load React component: no such component in Library ' +
          componentName,
      );
      return null;
    }
  });

  return <React.Fragment>{portals}</React.Fragment>;
};
