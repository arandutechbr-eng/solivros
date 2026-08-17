import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useEffect } from "react";

interface ParagraphEditorProps {
  content: string;
  onChange: (value: string) => void;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\n", "</p><p>");
}

export function ParagraphEditor({ content, onChange }: ParagraphEditorProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: `<p>${escapeHtml(content)}</p>`,
    editorProps: {
      attributes: {
        class: "min-h-[4.5rem] px-3 py-2 text-slate-800 focus:outline-none",
      },
    },
    onUpdate: ({ editor: current }) => {
      onChange(current.getText());
    },
  });

  useEffect(() => {
    if (!editor) return;
    const current = editor.getText();
    if (current !== content) {
      editor.commands.setContent(`<p>${escapeHtml(content)}</p>`);
    }
  }, [content, editor]);

  return <EditorContent editor={editor} />;
}
