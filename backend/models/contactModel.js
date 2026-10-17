/**
 * Contact Model (Supabase Integration)
 * Persists contact form inquiries into Supabase 'contact_messages' table.
 */

const { supabase, isSupabaseConnected, inMemoryStore } = require('../services/supabaseClient');

/**
 * Save contact message
 */
async function saveMessage({ name, email, message, status = 'sent' }) {
  const record = {
    name,
    email,
    message,
    status,
    created_at: new Date().toISOString()
  };

  if (isSupabaseConnected()) {
    try {
      const { data, error } = await supabase
        .from('contact_messages')
        .insert([record])
        .select()
        .single();

      if (!error) {
        return { success: true, id: data?.id };
      }
      console.warn('⚠️ Supabase error saving message:', error.message);
    } catch (err) {
      console.warn('⚠️ Supabase exception saving message:', err.message);
    }
  }

  // In-memory fallback
  inMemoryStore.messages.push(record);
  return { success: true, id: inMemoryStore.messages.length };
}

module.exports = {
  saveMessage
};
