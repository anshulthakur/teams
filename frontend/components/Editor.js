import React, { useRef , useEffect } from 'react';
import {
  BlockTypeSelect,
  CodeToggle,
  CreateLink,
  codeBlockPlugin,
  linkDialogPlugin,
  linkPlugin,
  DiffSourceToggleWrapper,
  InsertCodeBlock,
  InsertImage,
  diffSourcePlugin,
  imagePlugin,
  InsertTable,
  ListsToggle,
  headingsPlugin,
  listsPlugin,
  quotePlugin,
  thematicBreakPlugin,
  markdownShortcutPlugin,
  UndoRedo,
  BoldItalicUnderlineToggles,
  toolbarPlugin,
  tablePlugin,
  codeMirrorPlugin,
  KitchenSinkToolbar,
  CodeMirrorEditor,
  MDXEditor,
} from '@mdxeditor/editor';

import '@mdxeditor/editor/style.css'; // Import the styles

const plugins = [
  headingsPlugin({ allowedHeadingLevels: [1, 2, 3] }),
  listsPlugin(),
  quotePlugin(),
  imagePlugin(),
  linkDialogPlugin(),
  tablePlugin(),
  diffSourcePlugin(),
  thematicBreakPlugin(),
  markdownShortcutPlugin(),
  codeMirrorPlugin({ codeBlockLanguages: { txt: 'text',
                                            js: 'JavaScript',
                                            ts: 'TypeScript',
                                            tsx: 'TypeScript (React)',
                                            jsx: 'JavaScript (React)',
                                            css: 'CSS',
                                            python: 'Python',
                                            bash: 'Bash',
                                            cpp: 'C/C++' } }),
  codeBlockPlugin({ defaultCodeBlockLanguage: 'text' ,
                    codeBlockEditorDescriptors: [{
                      priority: 100,
                      match: () => true,
                      Editor: CodeMirrorEditor,
                    }],
                  }),
  toolbarPlugin({ toolbarContents: () => <KitchenSinkToolbar /> }),
  DiffSourceToggleWrapper
];

const Editor = ({ markdown, onChange, placeholder = 'Enter content' }) => {
  const editorRef = useRef(null); // Reference to the editor instance

  useEffect(() => {
    if (editorRef.current && markdown) {
      editorRef.current.setMarkdown(markdown); // Set the initial markdown content
    }
  }, [markdown]);

  const handleChange = (newMarkdown) => {
    if (onChange) {
      clearTimeout(window.editorChangeTimeout);
      window.editorChangeTimeout = setTimeout(() => onChange(newMarkdown), 300); // Notify the parent about changes
    }
  };

  const onError = (payload) => {
    console.log(payload);
  }

  return (
    <MDXEditor
      ref={editorRef} // Attach the editor instance to the reference
      plugins={plugins}
      markdown="" // Initialize with blank markdown
      onChange={handleChange}
      trim={false}
      onError={onError}
      placeholder={placeholder}
    />
  );
};

export default Editor;
